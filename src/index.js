import { BaseReactPyClient, mount } from "@reactpy/client";
import { DOMWidgetView } from "@jupyter-widgets/base";

/** @param view {DOMWidgetView} view */
export function render(view) {
  const client = new JupyterReactPyClient(view);
  mount(view.el, client);
}

let viewID = 0;

class JupyterReactPyClient extends BaseReactPyClient {
  /**
   * @param view {DOMWidgetView}
   * @param viewID {number}
   */
  constructor(view, viewId) {
    super();
    this.view = view;
    this.viewID = viewID++;

    if (jupyterServerBaseUrl) {
      this.importSourceBaseUrl = concatAndResolveUrl(
        jupyterServerBaseUrl,
        "_reactpy_web_modules"
      );
    } else {
      this.importSourceBaseUrl = this.model.attributes._import_source_base_url;
    }
    if (!this.importSourceBaseUrl) {
      console.error(
        "No Jupyter Server base URL could be discovered and no import source base URL was configured."
      );
    }

    this.ready.then(() => {
      this.view.send({
        type: "client-ready",
        viewID: this.viewID,
        data: null,
      });
    });

    this.view.model.on("msg:custom", (msg) => {
      if (msg.viewID == this.viewID) {
        this.handleIncoming(msg.data);
      }
    });

    this.view.on("remove", () => {
      this.view.model.send({
        type: "client-removed",
        viewID: this.viewID,
        data: null,
      });
    });
  }

  /** @param message {any} */
  sendMessage(message) {
    this.view.model.send({
      type: "dom-event",
      viewID: this.viewID,
      data: message,
    });
  }

  /** @param moduleName {string} */
  loadModule(moduleName) {
    return import(`${this.importSourceBaseUrl}/${moduleName}`);
  }
}

const jupyterServerBaseUrl = (() => {
  const jupyterConfig = document.getElementById("jupyter-config-data");
  if (jupyterConfig) {
    return JSON.parse(jupyterConfig.text)["baseUrl"];
  }
  return document.getElementsByTagName("body")[0].getAttribute("data-base-url");
})();

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
