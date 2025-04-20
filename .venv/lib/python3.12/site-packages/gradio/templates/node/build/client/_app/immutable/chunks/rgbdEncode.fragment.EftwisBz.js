import { j as ShaderStore } from "./index.Bq5mFuDo.js";
import "./helperFunctions.GtpVj9KP.js";
const name = "rgbdEncodePixelShader";
const shader = `varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=toRGBD(texture2D(textureSampler,vUV).rgb);}`;
if (!ShaderStore.ShadersStore[name]) {
  ShaderStore.ShadersStore[name] = shader;
}
const rgbdEncodePixelShader = { name, shader };
export {
  rgbdEncodePixelShader
};
