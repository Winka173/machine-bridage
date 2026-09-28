using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>One model's page in the impostor atlas for one army: the model from the game's camera angle at <see cref="ImpostorAtlas.Headings"/> headings.</summary>
    public sealed class ImpostorPage
    {
        internal ImpostorPage(string model, int team, int sheet, int slot, Vector3 centre, float radius)
        {
            Model = model;
            Team = team;
            Sheet = sheet;
            Slot = slot;
            Centre = centre;
            Radius = radius;
        }

        /// <summary>The resolved model id and the army whose colours it wears (0, 1, or 2 for everyone else).</summary>
        public string Model { get; }
        public int Team { get; }

        /// <summary>Which sheet it is on, and where (row-major, <see cref="ImpostorAtlas.PagesPerRow"/> a row).</summary>
        public int Sheet { get; }
        public int Slot { get; }

        /// <summary>The point the card is centred on (on the model's upright axis, model units) and half its side.</summary>
        public Vector3 Centre { get; }
        public float Radius { get; }

        /// <summary>Drawn into the atlas; until then its vehicles keep their meshes.</summary>
        public bool Baked { get; internal set; }

        /// <summary>UV of the lower-left corner of heading <paramref name="heading"/>'s cell.</summary>
        public Vector2 Cell(int heading)
        {
            heading = ((heading % ImpostorAtlas.Headings) + ImpostorAtlas.Headings) % ImpostorAtlas.Headings;
            var page = new Vector2(Slot % ImpostorAtlas.PagesPerRow, Slot / ImpostorAtlas.PagesPerRow) * ImpostorAtlas.PagePixels;
            var cell = new Vector2(heading % ImpostorAtlas.PageCells, heading / ImpostorAtlas.PageCells) * ImpostorAtlas.CellPixels;
            return (page + cell) / ImpostorAtlas.SheetPixels;
        }
    }

    /// <summary>
    /// Pre-rendered cards for vehicles too small on screen for meshes (<see cref="VehicleLod.Impostor"/>).
    /// For each model and army a page of sixteen headings is drawn from the far detail level with
    /// the game camera's rotation, storing albedo and coverage in one texture and the view-space
    /// normal, metallic and glow in another, so the cards are lit live (<c>MachineBrigade/Impostor</c>).
    /// Pages are asked for when a vehicle is made and drawn a few a frame; sheets of sixteen pages
    /// are added as needed, and all the cards on a sheet go in one instanced draw.
    /// </summary>
    public sealed class ImpostorAtlas : IDisposable
    {
        public const int Headings = 16;
        public const int CellPixels = 32;
        public const int PageCells = 4;
        public const int PagePixels = CellPixels * PageCells;
        public const int SheetPixels = 512;
        public const int PagesPerRow = SheetPixels / PagePixels;
        public const int PagesPerSheet = PagesPerRow * PagesPerRow;

        /// <summary>A little room round the model in its cells, so mip levels do not pull in the neighbours.</summary>
        private const float Margin = 1.06f;

        private const int MaxBatch = 511;

        private static readonly int AlbedoId = Shader.PropertyToID("_Albedo");
        private static readonly int SurfaceId = Shader.PropertyToID("_Surface");
        private static readonly int CellsId = Shader.PropertyToID("_ImpCells");
        private static readonly int ShapeId = Shader.PropertyToID("_ImpShape");
        private static readonly int TintId = Shader.PropertyToID("_ImpTint");
        private static readonly int ViewToWorldId = Shader.PropertyToID("_MbImpostorViewToWorld");

        private sealed class Sheet
        {
            public RenderTexture Albedo, Surface;
            public Material Material;
            public bool Dirty;
            public readonly List<Matrix4x4> Matrices = new();
            public readonly List<Vector4> Cells = new(), Shapes = new(), Tints = new();
        }

        private readonly MaterialLibrary _materials;
        private readonly Dictionary<(string, int), ImpostorPage> _pages = new();
        private readonly Dictionary<ImpostorPage, ModelLod> _sources = new();
        private readonly Queue<ImpostorPage> _pending = new();
        private readonly List<Sheet> _sheets = new();
        private readonly Shader _shader;
        private readonly bool _gpu;
        private RenderTexture _depth;
        private CommandBuffer _commands;
        private Mesh _quad;
        private MaterialPropertyBlock _block;
        private Quaternion _bakedRotation = Quaternion.identity;
        private readonly Matrix4x4[] _batch = new Matrix4x4[MaxBatch];
        private readonly Vector4[] _batchCells = new Vector4[MaxBatch], _batchShapes = new Vector4[MaxBatch], _batchTints = new Vector4[MaxBatch];

        public ImpostorAtlas(MaterialLibrary materials)
        {
            _materials = materials;
            _shader = Shader.Find("MachineBrigade/Impostor");
            // Batch mode without graphics lays pages out and marks them drawn, so the logic can be tested.
            _gpu = SystemInfo.graphicsDeviceType != GraphicsDeviceType.Null && _shader != null;
        }

        /// <summary>Pages so far (every model and army asked for).</summary>
        public IReadOnlyCollection<ImpostorPage> Pages => _pages.Values;

        public int SheetCount => _sheets.Count;

        /// <summary>Pages asked for and not drawn yet.</summary>
        public int PendingCount => _pending.Count;

        /// <summary>Cards drawn by the last <see cref="Flush"/>.</summary>
        public int LastDrawn { get; private set; }

        /// <summary>Draws issued by the last <see cref="Flush"/> (one per sheet with cards on it).</summary>
        public int LastDraws { get; private set; }

        /// <summary>The army a page is kept for: the player, the enemy, or one shared by everyone else.</summary>
        public static int PageTeam(int team) => team is 0 or 1 ? team : 2;

        /// <summary>A model's page for an army; made (and queued for drawing) on first request. Null without a far detail level.</summary>
        public ImpostorPage Request(ModelLod lod, int team)
        {
            if (lod == null || lod.BakeParts.Count == 0) return null;
            team = PageTeam(team);
            if (_pages.TryGetValue((lod.Id, team), out var page)) return page;
            var index = _pages.Count;
            var sheet = index / PagesPerSheet;
            while (_sheets.Count <= sheet) _sheets.Add(NewSheet());
            // The card turns with the model about its upright axis: centre it there, big enough for any heading.
            var b = lod.BakeBounds;
            var centre = new Vector3(0f, b.center.y, 0f);
            var reach = 0f;
            for (var i = 0; i < 8; i++)
            {
                var corner = new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y, (i & 4) == 0 ? b.min.z : b.max.z);
                reach = Mathf.Max(reach, (corner - centre).magnitude);
            }
            page = new ImpostorPage(lod.Id, team, sheet, index % PagesPerSheet, centre, reach * Margin);
            _pages[(lod.Id, team)] = page;
            _sources[page] = lod;
            _pending.Enqueue(page);
            return page;
        }

        /// <summary>Draws up to <paramref name="budget"/> queued pages into the atlas, seen with the game camera's <paramref name="cameraRotation"/>.</summary>
        public void BakePending(Quaternion cameraRotation, int budget = 2)
        {
            if (_pending.Count == 0) return;
            _bakedRotation = cameraRotation;
            if (!_gpu)
            {
                while (_pending.Count > 0 && budget-- > 0) _pending.Dequeue().Baked = true;
                return;
            }
            _commands ??= new CommandBuffer { name = "Impostor Bake" };
            _commands.Clear();
            if (_depth == null)
            {
                _depth = new RenderTexture(SheetPixels, SheetPixels, 24, RenderTextureFormat.Depth) { name = "Impostor Depth" };
                _depth.Create();
            }
            var baked = new List<ImpostorPage>();
            while (_pending.Count > 0 && budget-- > 0)
            {
                var page = _pending.Dequeue();
                Bake(page, _sources[page], cameraRotation);
                baked.Add(page);
            }
            foreach (var sheet in _sheets)
            {
                if (!sheet.Dirty) continue;
                sheet.Dirty = false;
                _commands.GenerateMips(sheet.Albedo);
                _commands.GenerateMips(sheet.Surface);
            }
            Graphics.ExecuteCommandBuffer(_commands);
            foreach (var page in baked) page.Baked = true;
        }

        private void Bake(ImpostorPage page, ModelLod lod, Quaternion rotation)
        {
            var sheet = _sheets[page.Sheet];
            var cmd = _commands;
            cmd.SetRenderTarget(new RenderTargetIdentifier[] { sheet.Albedo, sheet.Surface }, _depth);
            // The depth buffer is shared by every sheet: clear all of it (a viewport may be left from the last page).
            cmd.SetViewport(new Rect(0f, 0f, SheetPixels, SheetPixels));
            cmd.ClearRenderTarget(true, false, Color.clear);
            var r = page.Radius;
            var eye = page.Centre - rotation * Vector3.forward * (r + 5f);
            var view = Matrix4x4.Scale(new Vector3(1f, 1f, -1f)) * Matrix4x4.TRS(eye, rotation, Vector3.one).inverse;
            cmd.SetViewProjectionMatrices(view, Matrix4x4.Ortho(-r, r, -r, r, 0.1f, 2f * r + 10f));
            var material = _materials.LodSurface(page.Team);
            var pass = material.FindPass("ImpostorBake");
            if (pass < 0) return;
            for (var k = 0; k < Headings; k++)
            {
                var corner = page.Cell(k) * SheetPixels;
                cmd.SetViewport(new Rect(corner.x, corner.y, CellPixels, CellPixels));
                var yaw = Matrix4x4.Rotate(Quaternion.Euler(0f, k * 360f / Headings, 0f));
                foreach (var (mesh, local) in lod.BakeParts) cmd.DrawMesh(mesh, yaw * local, material, 0, pass);
            }
            sheet.Dirty = true;
        }

        private Sheet NewSheet()
        {
            var sheet = new Sheet();
            if (!_gpu) return sheet;
            RenderTexture Target(string name, RenderTextureReadWrite space)
            {
                var rt = new RenderTexture(SheetPixels, SheetPixels, 0, RenderTextureFormat.ARGB32, space)
                {
                    name = name,
                    useMipMap = true,
                    autoGenerateMips = false,
                    filterMode = FilterMode.Trilinear,
                    wrapMode = TextureWrapMode.Clamp,
                };
                rt.Create();
                return rt;
            }
            sheet.Albedo = Target($"Impostor Albedo {_sheets.Count}", RenderTextureReadWrite.sRGB);
            sheet.Surface = Target($"Impostor Surface {_sheets.Count}", RenderTextureReadWrite.Linear);
            var clear = new CommandBuffer { name = "Impostor Clear" };
            foreach (var target in new[] { sheet.Albedo, sheet.Surface })
            {
                clear.SetRenderTarget(target);
                clear.ClearRenderTarget(false, true, Color.clear);
            }
            Graphics.ExecuteCommandBuffer(clear);
            clear.Release();
            sheet.Material = new Material(_shader) { name = $"Impostor {_sheets.Count}", enableInstancing = true };
            sheet.Material.SetTexture(AlbedoId, sheet.Albedo);
            sheet.Material.SetTexture(SurfaceId, sheet.Surface);
            return sheet;
        }

        /// <summary>Starts a frame's cards.</summary>
        public void Begin()
        {
            foreach (var sheet in _sheets)
            {
                sheet.Matrices.Clear();
                sheet.Cells.Clear();
                sheet.Shapes.Clear();
                sheet.Tints.Clear();
            }
        }

        /// <summary>
        /// One card: <paramref name="page"/>'s model with its upright axis through
        /// <paramref name="centre"/> (world), drawn <paramref name="scale"/> times its model size,
        /// facing <paramref name="yawDegrees"/>, tinted (rgb) and flashing (1 - a).
        /// </summary>
        public void Add(ImpostorPage page, Vector3 centre, float scale, float yawDegrees, Color tint)
        {
            if (page == null || !page.Baked || page.Sheet >= _sheets.Count) return;
            var sheet = _sheets[page.Sheet];
            var f = Mathf.Repeat(yawDegrees, 360f) / (360f / Headings);
            var k = Mathf.FloorToInt(f);
            var a = page.Cell(k);
            var b = page.Cell(k + 1);
            var size = page.Radius * 2f * scale;
            sheet.Matrices.Add(Matrix4x4.TRS(centre, Quaternion.identity, new Vector3(size, size, size)));
            sheet.Cells.Add(new Vector4(a.x, a.y, b.x, b.y));
            sheet.Shapes.Add(new Vector4(f - k, (float)CellPixels / SheetPixels, page.Radius * scale, 0f));
            sheet.Tints.Add(tint);
        }

        /// <summary>Draws the frame's cards, one instanced draw per sheet (per <see cref="MaxBatch"/> cards).</summary>
        public void Flush()
        {
            LastDrawn = 0;
            LastDraws = 0;
            if (!_gpu)
            {
                foreach (var sheet in _sheets) LastDrawn += sheet.Matrices.Count;
                return;
            }
            _quad ??= Quad();
            _block ??= new MaterialPropertyBlock();
            // Baked normals are in the atlas camera's space.
            Shader.SetGlobalMatrix(ViewToWorldId, Matrix4x4.Rotate(_bakedRotation) * Matrix4x4.Scale(new Vector3(1f, 1f, -1f)));
            foreach (var sheet in _sheets)
            {
                for (var start = 0; start < sheet.Matrices.Count; start += MaxBatch)
                {
                    var count = Mathf.Min(MaxBatch, sheet.Matrices.Count - start);
                    sheet.Matrices.CopyTo(start, _batch, 0, count);
                    sheet.Cells.CopyTo(start, _batchCells, 0, count);
                    sheet.Shapes.CopyTo(start, _batchShapes, 0, count);
                    sheet.Tints.CopyTo(start, _batchTints, 0, count);
                    _block.Clear();
                    _block.SetVectorArray(CellsId, _batchCells);
                    _block.SetVectorArray(ShapeId, _batchShapes);
                    _block.SetVectorArray(TintId, _batchTints);
                    var rp = new RenderParams(sheet.Material)
                    {
                        matProps = _block,
                        shadowCastingMode = ShadowCastingMode.Off,
                        receiveShadows = true,
                        worldBounds = new Bounds(Vector3.zero, Vector3.one * 5000f),
                    };
                    Graphics.RenderMeshInstanced(rp, _quad, 0, _batch, count);
                    LastDrawn += count;
                    LastDraws++;
                }
            }
        }

        /// <summary>A unit card in its own XY plane (the shader turns it to the camera).</summary>
        private static Mesh Quad()
        {
            var mesh = new Mesh { name = "Impostor Card" };
            mesh.SetVertices(new[] { new Vector3(-0.5f, -0.5f, 0f), new Vector3(0.5f, -0.5f, 0f), new Vector3(0.5f, 0.5f, 0f), new Vector3(-0.5f, 0.5f, 0f) });
            mesh.SetTriangles(new[] { 0, 2, 1, 0, 3, 2 }, 0);
            mesh.bounds = new Bounds(Vector3.zero, Vector3.one * 2f);
            return mesh;
        }

        /// <summary>The atlas sheets as they are, for checking by eye (editor tools).</summary>
        internal IEnumerable<(RenderTexture albedo, RenderTexture surface)> Sheets()
        {
            foreach (var sheet in _sheets) yield return (sheet.Albedo, sheet.Surface);
        }

        public void Dispose()
        {
            foreach (var sheet in _sheets)
            {
                Release(sheet.Albedo);
                Release(sheet.Surface);
                Release(sheet.Material);
            }
            _sheets.Clear();
            Release(_depth);
            Release(_quad);
            _commands?.Release();
            _commands = null;
            _pages.Clear();
            _sources.Clear();
            _pending.Clear();
        }

        private static void Release(Object o)
        {
            if (o == null) return;
            if (o is RenderTexture rt) rt.Release();
            if (Application.isPlaying) Object.Destroy(o);
            else Object.DestroyImmediate(o);
        }
    }
}
