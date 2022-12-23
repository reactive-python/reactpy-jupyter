import { IdomModel, IdomView, version } from "./index";
import { IJupyterWidgetRegistry } from "@jupyter-widgets/base";

export const idomWidgetPlugin = {
  id: "idom-client-jupyter:plugin",
  requires: [IJupyterWidgetRegistry],
  activate: function (app, widgets) {
    widgets.registerWidget({
      name: "idom-client-jupyter",
      version: version,
      exports: { IdomModel, IdomView },
    });
  },
  autoStart: true,
};

export default idomWidgetPlugin;
