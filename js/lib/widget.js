import { DOMWidgetModel, DOMWidgetView } from "@jupyter-widgets/base";
import { mountLayout } from "idom-client-react";

export class IdomModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: "IdomModel",
      _view_name: "IdomView",
      _model_module: "idom-client-jupyter",
      _view_module: "idom-client-jupyter",
      _model_module_version: "0.9.1",
      _view_module_version: "0.9.1",
    };
  }
}

var _nextViewID = { id: 0 };

const jupyterServerBaseUrl = (() => {
  const jupyterConfig = document.getElementById("jupyter-config-data");
  if (jupyterConfig) {
    return JSON.parse(jupyterConfig.text)["baseUrl"];
  }
  return document.getElementsByTagName("body")[0].getAttribute("data-base-url");
})();

export class IdomView extends DOMWidgetView {
  constructor(options) {
    super(options);
    this.render = this.render.bind(this);
    this.remove = this.remove.bind(this);
  }

  render() {
    this.viewID = _nextViewID.id;
    _nextViewID.id++;

    var saveUpdateHook = (updateHook) => {
      this.model.on("msg:custom", (msg, buffers) => {
        if (msg.viewID == this.viewID) {
          updateHook(...msg.data);
        }
      });
      this.send({
        type: "client-ready",
        viewID: this.viewID,
        data: null,
      });
    };

    var sendEvent = (event) => {
      this.send({
        type: "dom-event",
        viewID: this.viewID,
        data: event,
      });
    };

    let importSourceBaseUrl;
    if (jupyterServerBaseUrl) {
      importSourceBaseUrl = concatAndResolveUrl(
        jupyterServerBaseUrl,
        "_idom_web_modules"
      );
    } else {
      importSourceBaseUrl = this.model.attributes._import_source_base_url;
    }
    if (!importSourceBaseUrl) {
      console.error(
        "No Jupyter Server base URL could be discovered and no import source base URL was configured."
      );
    }

    var loadImportSource = (source, sourceType) => {
      return import(
        /* webpackIgnore: true */
        sourceType == "NAME" ? `${importSourceBaseUrl}/${source}` : source
      );
    };

    mountLayout(this.el, {
      saveUpdateHook,
      sendEvent,
      loadImportSource,
    });
  }

  remove() {
    this.send({ type: "client-removed", viewID: this.viewID });
    return super.remove();
  }
}

function concatAndResolveUrl(url, concat) {
  var url1 = (url.endsWith("/") ? url.slice(0, -1) : url).split("/");
  var url2 = concat.split("/");
  var url3 = [];
  for (var i = 0, l = url1.length; i < l; i++) {
    if (url1[i] == "..") {
      url3.pop();
    } else if (url1[i] == ".") {
      continue;
    } else {
      url3.push(url1[i]);
    }
  }
  for (var i = 0, l = url2.length; i < l; i++) {
    if (url2[i] == "..") {
      url3.pop();
    } else if (url2[i] == ".") {
      continue;
    } else {
      url3.push(url2[i]);
    }
  }
  return url3.join("/");
}
