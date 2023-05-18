/**
 * @typedef {import("@jupyter-widgets/base").DOMWidgetView} DOMWidgetView
 */
import { BaseReactPyClient, mount } from "@reactpy/client";

/**@param view {DOMWidgetView} view */
export function render(view) {
  const client = new JupyterReactPyClient(view);
  mount(view.el, client);

  async function updateInnerWidgets() {
    /** @type {String[]} */
    let innerModelIds = view.model.get("_inner_widgets");

    for (let modelId of innerModelIds.map((id) =>
      id.slice("IPY_MODEL_".length)
    )) {
      let model = await view.model.widget_manager.get_model(modelId);
      (await waitForSelectorAll(`.widget-model-id-${modelId}`, view.el)).map(
        async (containerEl) => {
          let childView = await view.create_child_view(model);
          containerEl.replaceChildren(childView.el);
        }
      );
    }
  }

  view.model.on("change:_inner_widgets", updateInnerWidgets);

  updateInnerWidgets();
}

let viewID = 0;

class JupyterReactPyClient extends BaseReactPyClient {
  /**
   * @param view {DOMWidgetView}
   */
  constructor(view) {
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
  async loadModule(moduleName) {
    // Because import() does not behave directly when running via AnyWidgets. This is
    // because this code is itself imported and executed via a dynamic import() whose
    // source is a URL constructed by URL.createObjectURL. This appears to impact both
    // path resolution as well as CORS. By constrast the fetch() API does not appear to
    // be impacted by this. So we use fetch() to get the module source instead.
    const rsp = await fetch(`${this.importSourceBaseUrl}/${moduleName}`);
    return await import(URL.createObjectURL(await rsp.blob()));
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
  let url1 = (url.endsWith("/") ? url.slice(0, -1) : url).split("/");
  let url2 = concat.split("/");
  let url3 = [];
  for (let i = 0, l = url1.length; i < l; i++) {
    if (url1[i] == "..") {
      url3.pop();
    } else if (url1[i] == ".") {
      continue;
    } else {
      url3.push(url1[i]);
    }
  }
  for (let i = 0, l = url2.length; i < l; i++) {
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

/**
 * @param {String} selector
 * @param {HTMLElement} containerElement
 * @returns {Promise<Element[]>}
 */
function waitForSelectorAll(selector, containerElement) {
  return new Promise((resolve) => {
    const resolveSearch = () => {
      const elements = Array.from(document.querySelectorAll(selector));
      if (elements.length) {
        resolve(elements);
        return true;
      }
      return false;
    };

    if (resolveSearch()) {
      return;
    }

    const observer = new MutationObserver(() =>
      resolveSearch() ? observer.disconnect() : null
    );

    observer.observe(containerElement, {
      childList: true,
      subtree: true,
    });
  });
}
