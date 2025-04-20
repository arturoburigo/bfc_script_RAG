import { c as RichTypeBoolean } from "./declarationMapper.ClcoZIzq.js";
import { f as FlowGraphExecutionBlock } from "./KHR_interactivity.DhQWS96m.js";
import { R as RegisterClass } from "./index.Bq5mFuDo.js";
class FlowGraphBranchBlock extends FlowGraphExecutionBlock {
  constructor(config) {
    super(config);
    this.condition = this.registerDataInput("condition", RichTypeBoolean);
    this.onTrue = this._registerSignalOutput("onTrue");
    this.onFalse = this._registerSignalOutput("onFalse");
  }
  _execute(context) {
    if (this.condition.getValue(context)) {
      this.onTrue._activateSignal(context);
    } else {
      this.onFalse._activateSignal(context);
    }
  }
  /**
   * @returns class name of the block.
   */
  getClassName() {
    return "FlowGraphBranchBlock";
  }
}
RegisterClass("FlowGraphBranchBlock", FlowGraphBranchBlock);
export {
  FlowGraphBranchBlock
};
