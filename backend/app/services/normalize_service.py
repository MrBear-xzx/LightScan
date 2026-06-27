from app.plugins.scanner.nuclei_json import NucleiJsonScannerPlugin


def normalize_nuclei_results(raw_results: list[dict]) -> list[dict]:
    plugin = NucleiJsonScannerPlugin()
    return [plugin.normalize(item) for item in raw_results]
