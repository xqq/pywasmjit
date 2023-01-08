importScripts('https://cdn.jsdelivr.net/pyodide/v0.22.0/full/pyodide.js');

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide({
        stderr: (msg) => postOutput(msg + '\n'),
        stdout: (msg) => postOutput(msg + '\n')
    });
    await pyodide.loadPackage('../dist/pywasmjit-0.1.0-py3-none-any.whl');
    self.postMessage({
        type: 'initialized'
    });
}

let pyodideReadyPromise = loadPyodideAndPackages();

function postOutput(text) {
    self.postMessage({
        type: 'output',
        text: text,
    });
}

function makeid(length) {
    let result = '';
    const prefix_dict = 'abcdefghijklmnopqrstuvwxyz';
    const dict = 'abcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < length; i++ ) {
        if (i == 0) {
            result += prefix_dict.charAt(Math.floor(Math.random() * prefix_dict.length))
        } else {
            result += dict.charAt(Math.floor(Math.random() * dict.length));
        }
    }
    return result;
}

async function runScript(id, source) {
    let module_name = makeid(8);
    let filename = `${module_name}.py`;
    pyodide.FS.writeFile(filename, source);

    self.postMessage({
        type: 'exec_start',
        id: id,
    });

    await pyodide.runPythonAsync(`
        import sys
        import importlib.machinery
        import importlib.util
        import pywasmjit

        class ForceFlusher:
            def __init__(self, output):
                self.output = output

            def __getattr__(self, attr):
                if attr == 'write':
                    return ForceFlusher.write
                else:
                    return getattr(self.output, attr)

            def write(self, text):
                self.output.write(text)
                self.output.flush()

        sys.stdout = ForceFlusher(sys.stdout)
        sys.stderr = ForceFlusher(sys.stderr)

        loader = importlib.machinery.SourceFileLoader(\"${module_name}\", \"${filename}\")
        spec = importlib.util.spec_from_loader(\"${module_name}\", loader )
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)

        del(module)
        pywasmjit.cleanup()
        `);

    self.postMessage({
        type: 'exec_finished',
        id: id,
    });
}

self.onmessage = async (e) => {
    await pyodideReadyPromise;

    if (e.data.type == 'execute') {
        let id = e.data.id;
        let source = e.data.data;
        try {
            await runScript(id, source);
        } catch (e) {
            self.postMessage({
                type: 'exec_error',
                id: id,
                error: e.message,
            });
        }
    }
}
