import argparse
import json
import os
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from google import genai

MODEL = "gemini-2.5-flash"

SCHEMA = {
    "type": "object",
    "properties": {
        "descricao_curta": {"type": "string"},
        "objetos": {"type": "array", "items": {"type": "string"}},
        "texto_visivel": {"type": "string"},
        "sensivel": {"type": "boolean"},
        "confianca": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "descricao_curta",
        "objetos",
        "texto_visivel",
        "sensivel",
        "confianca",
    ],
    "additionalProperties": False,
}

PROMPT = (
    "Analise esta imagem recuperada por file carving. "
    "Descreva o conteudo visual, objetos principais, texto visivel (OCR simples) "
    "e se parece sensivel. Responda apenas no JSON do schema."
)


def analyze_one(client: genai.Client, image_path: Path) -> dict:
    with Image.open(image_path) as image:
        response = client.models.generate_content(
            model=MODEL,
            contents=[image, PROMPT],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": SCHEMA,
            },
        )

    return json.loads(response.text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analisa JPGs recuperados com Gemini e salva resultados em JSONL."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Pasta com arquivos JPG recuperados.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Arquivo JSONL de saida (padrao: <input>/analise.jsonl).",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    out_file = Path(args.out) if args.out else input_dir / "analise.jsonl"

    if not input_dir.is_dir():
        raise SystemExit(f"Diretorio invalido: {input_dir}")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Defina GEMINI_API_KEY antes de executar.")

    client = genai.Client(api_key=api_key)
    files = sorted(input_dir.glob("*.jpg"))

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as handle:
        for image_path in files:
            try:
                result = analyze_one(client, image_path)
                result["arquivo"] = str(image_path)
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
                print(f"OK: {image_path.name}")
            except UnidentifiedImageError:
                print(f"IGNORADO (JPEG invalido/corrompido): {image_path.name}")
            except Exception as exc:
                print(f"ERRO em {image_path.name}: {exc}")

    print(f"Analise finalizada. Resultado em: {out_file}")


if __name__ == "__main__":
    main()
