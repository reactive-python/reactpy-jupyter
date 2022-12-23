import { HelloModel, HelloView, version } from "./index";
import { IJupyterWidgetRegistry } from "@jupyter-widgets/base";

export const helloWidgetPlugin = {
  id: "idom-client-jupyter:plugin",
  requires: [IJupyterWidgetRegistry],
  activate: function (app, widgets) {
    widgets.registerWidget({
      name: "idom-client-jupyter",
      version: version,
      exports: { HelloModel, HelloView },
    });
  },
  autoStart: true,
};

export default helloWidgetPlugin;
