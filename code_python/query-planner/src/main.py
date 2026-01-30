import argparse
import json
import sys
from .parser import parse_query
from .optimizer import optimize
from .compiler import compile_to_sql

def main():
    parser = argparse.ArgumentParser(description="Query Planner & Optimizer")
    parser.add_argument("query_file", help="Path to JSON query file")
    parser.add_argument("--no-opt", action="store_true", help="Disable optimization")
    args = parser.parse_args()

    try:
        with open(args.query_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # 1. Parse
        ast = parse_query(data)

        # 2. Optimize (optional)
        if not args.no_opt:
            ast = optimize(ast)

        # 3. Compile
        sql = compile_to_sql(ast)
        print(sql)

    except Exception as e:
        print(f"Error processing query: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
