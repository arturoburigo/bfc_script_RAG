import { j as ShaderStore } from "./index.Bq5mFuDo.js";
import "./helperFunctions.GtpVj9KP.js";
const name = "rgbdDecodePixelShader";
const shader = `varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;
if (!ShaderStore.ShadersStore[name]) {
  ShaderStore.ShadersStore[name] = shader;
}
const rgbdDecodePixelShader = { name, shader };
export {
  rgbdDecodePixelShader
};
