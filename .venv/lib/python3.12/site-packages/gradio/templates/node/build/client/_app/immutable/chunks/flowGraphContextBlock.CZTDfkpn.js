import { F as FlowGraphBlock } from "./KHR_interactivity.DhQWS96m.js";
import { R as RichTypeAny, b as RichTypeNumber } from "./declarationMapper.ClcoZIzq.js";
import { R as RegisterClass } from "./index.Bq5mFuDo.js";
class FlowGraphContextBlock extends FlowGraphBlock {
  constructor(config) {
    super(config);
    this.userVariables = this.registerDataOutput("userVariables", RichTypeAny);
    this.executionId = this.registerDataOutput("executionId", RichTypeNumber);
  }
  _updateOutputs(context) {
    this.userVariables.setValue(context.userVariables, context);
    this.executionId.setValue(context.executionId, context);
  }
  serialize(serializationObject) {
    super.serialize(serializationObject);
  }
  getClassName() {
    return "FlowGraphContextBlock";
  }
}
RegisterClass("FlowGraphContextBlock", FlowGraphContextBlock);
export {
  FlowGraphContextBlock
};
