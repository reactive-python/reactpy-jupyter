var widgets = require("@jupyter-widgets/base");
var _ = require("lodash");
var idomClientReact = require("idom-client-react");

// See example.py for the kernel counterpart to this file.
var IdomModel = widgets.DOMWidgetModel.extend({
  defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
    _model_name: "IdomModel",
    _view_name: "IdomView",
    _model_module: "idom-client-jupyter",
    _view_module: "idom-client-jupyter",
    _model_module_version: "0.1.0",
    _view_module_version: "0.1.0",
  }),
});

// Custom View. Renders the widget model.

var _viewID = { id: 0 };

class IdomView extends widgets.DOMWidgetView {
  // Defines how the widget gets rendered into the DOM
  render() {
    var id = _viewID.id;
    _viewID.id++;
    var saveUpdateHook = (updateHook) => {
      this.model.on("msg:custom", (update, buffers) => {
        updateHook(...update);
      });
      this.model.send({ type: "client-ready", id: id, data: null });
    };
    var sendEvent = (event) => {
      this.model.send({ type: "dom-event", id: id, data: event });
    };

    idomClientReact.mountLayout(this.el, saveUpdateHook, sendEvent);
  }
}

module.exports = {
  IdomModel: IdomModel,
  IdomView: IdomView,
};
