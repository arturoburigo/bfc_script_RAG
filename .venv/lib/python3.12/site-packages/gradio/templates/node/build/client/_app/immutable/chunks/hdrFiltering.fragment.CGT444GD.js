import { j as ShaderStore } from "./index.Bq5mFuDo.js";
import "./helperFunctions.GtpVj9KP.js";
import "./hdrFilteringFunctions.DvWC8L2A.js";
const name = "hdrFilteringPixelShader";
const shader = `#include<helperFunctions>
#include<importanceSampling>
#include<pbrBRDFFunctions>
#include<hdrFilteringFunctions>
uniform float alphaG;uniform samplerCube inputTexture;uniform vec2 vFilteringInfo;uniform float hdrScale;varying vec3 direction;void main() {vec3 color=radiance(alphaG,inputTexture,direction,vFilteringInfo);gl_FragColor=vec4(color*hdrScale,1.0);}`;
if (!ShaderStore.ShadersStore[name]) {
  ShaderStore.ShadersStore[name] = shader;
}
const hdrFilteringPixelShader = { name, shader };
export {
  hdrFilteringPixelShader
};
