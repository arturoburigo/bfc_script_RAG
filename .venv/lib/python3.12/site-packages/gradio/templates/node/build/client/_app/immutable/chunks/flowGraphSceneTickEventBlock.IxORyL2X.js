import { c as FlowGraphEventBlock } from "./KHR_interactivity.DhQWS96m.js";
import { R as RegisterClass } from "./index.Bq5mFuDo.js";
import { b as RichTypeNumber } from "./declarationMapper.ClcoZIzq.js";
class FlowGraphSceneTickEventBlock extends FlowGraphEventBlock {
  constructor() {
    super();
    this.type = "SceneBeforeRender";
    this.timeSinceStart = this.registerDataOutput("timeSinceStart", RichTypeNumber);
    this.deltaTime = this.registerDataOutput("deltaTime", RichTypeNumber);
  }
  /**
   * @internal
   */
  _preparePendingTasks(_context) {
  }
  /**
   * @internal
   */
  _executeEvent(context, payload) {
    this.timeSinceStart.setValue(payload.timeSinceStart, context);
    this.deltaTime.setValue(payload.deltaTime, context);
    this._execute(context);
    return true;
  }
  /**
   * @internal
   */
  _cancelPendingTasks(_context) {
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphSceneTickEventBlock";
  }
}
RegisterClass("FlowGraphSceneTickEventBlock", FlowGraphSceneTickEventBlock);
export {
  FlowGraphSceneTickEventBlock
};
