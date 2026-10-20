/** Render profile: how much scene the machine can afford (TODO68).

    The dashboard has to run on a workstation with a GPU and on a CI box
    without one. A software rasterizer (SwiftShader, llvmpipe) renders a
    1920x1080 shadowed scene in hundreds of milliseconds — enough to starve
    the browser's own event loop, so the WebSocket messages that carry the
    data arrive late or not at all.

    Detecting the rasterizer before the scene is built lets the dashboard
    spend the frame budget on the picture instead of on the wait.
*/

export interface RenderProfile {
  /** True when the WebGL implementation is a software rasterizer. */
  software: boolean;
  /** Frames per second the scene is allowed to spend. */
  fps: number;
  /** Whether the scene casts shadows. */
  shadows: boolean;
  /** Whether the WebGL context is antialiased. */
  antialias: boolean;
}

const SOFTWARE_RENDERER = /swiftshader|llvmpipe|software|basic render/i;

export function detectRenderProfile(): RenderProfile {
  const software = isSoftwareRenderer();
  return {
    software,
    fps: software ? 12 : 60,
    shadows: !software,
    antialias: !software,
  };
}

function isSoftwareRenderer(): boolean {
  try {
    const canvas = document.createElement("canvas");
    const gl =
      (canvas.getContext("webgl2") as WebGL2RenderingContext | null) ??
      (canvas.getContext("webgl") as WebGLRenderingContext | null);
    if (!gl) return true;
    const info = gl.getExtension("WEBGL_debug_renderer_info");
    const renderer = info
      ? String(gl.getParameter(info.UNMASKED_RENDERER_WEBGL))
      : String(gl.getParameter(gl.RENDERER));
    return SOFTWARE_RENDERER.test(renderer);
  } catch {
    return true;
  }
}
