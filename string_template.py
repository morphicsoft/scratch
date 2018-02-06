from pprint import pprint

import pystache

d = {
    "base_path": "/Data/base/",
    "build_name": "123",
    "box_path": "{{base_path}}{{build_name}}",
    "output_path": "{{box_path}}/output",
    "thingy": {
        "target_path": "{{output_path}}",
        "params": {
            "host": 2
        }
    }
}


def expand_config(d):
    def recur(k, v, accum, subaccum):
        if isinstance(v, dict):
            subaccum[k] = {k: recur(k, v, accum, {}) for k, v in v.items()}
            return subaccum[k]
        else:
            if isinstance(v, str):
                subaccum[k] = pystache.render(v, accum)
            else:
                subaccum[k] = v
            return subaccum[k]

    accum = {}
    for k, v in d.items():
        recur(k, v, accum, accum)
    return accum


if __name__ == '__main__':

    config = expand_config(d)
    pprint(config)
