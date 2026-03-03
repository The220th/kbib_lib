import argparse
from kbib_lib import form_bibs_from_yaml


def parse_args():
    parser = argparse.ArgumentParser(
        description="Python lib for forming bibliography. ")
    parser.add_argument("input_file", type=str,
                        help="Path to yaml with bibliography. ")
    parser.add_argument("output_file", type=str, help="Output file path")

    args = parser.parse_args()
    return args


def main():
    # [print(f"{i+1}) {el}") for i, el in enumerate(form_bibs_from_yaml("../examples/1.yaml"))]
    args = parse_args()
    s = "\n".join(form_bibs_from_yaml(args.input_file))
    with open(args.output_file, "w", encoding="utf-8") as fd:
        fd.write(s)
        fd.flush()


if __name__ == "__main__":
    main()
