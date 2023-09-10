class KwebAPI {
  constructor() {
    this.apiUrl = this.getApiUrl();
    this.init();
  }

  getApiUrl() {
    const urlParam = new URLSearchParams(window.location.search).get('apiUrl');
    if (urlParam) {
      localStorage.setItem('apiUrl', urlParam);
      return urlParam;
    }
    return localStorage.getItem('apiUrl') || 'https://kweb-api-py.gorbiz.repl.co';
  }

  init() {
    window.addEventListener('focusNode', (event) => {
      this.fetchNode(event.detail.id);
    });
    window.addEventListener('listNodes', () => {
      this.listNodes();
    });
    window.addEventListener('hashchange', () => {
      const id = window.location.hash.replace('#id=', '') || 'root';
      this.focusNode(id);
    });

    const id = window.location.hash.replace('#id=', '') || 'root';
    this.focusNode(id);
  }

  focusNode(id) {
    window.dispatchEvent(new CustomEvent('focusNode', { detail: { id } }));
  }

  listNodes() {
    window.dispatchEvent(new CustomEvent('listNodes'));
  }

  async fetchNode(id) {
    const res = await fetch(`${this.apiUrl}/nodes/${id}`);
    const data = await res.json();
    window.dispatchEvent(new CustomEvent('nodeLoaded', { detail: data }));
  }

  async listNodes() {
    const res = await fetch(`${this.apiUrl}/nodes/`);
    const data = await res.json();
    window.dispatchEvent(new CustomEvent('nodesListed', { detail: data }));
  }
}

const kweb = new KwebAPI();