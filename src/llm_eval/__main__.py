"""Entry point for python -m llm_eval"""
from llm_eval.cli import main
import typer

if __name__ == "__main__":
    typer.run(main)
