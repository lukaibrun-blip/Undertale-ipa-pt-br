from __future__ import annotations

import argparse
import plistlib
import sys
import zipfile
from pathlib import Path

DEFAULT_BUNDLE_ID = "com.jockeholm.undertale"
DEFAULT_VERSION = "2.0.0"
GAME_MAGIC_PREFIX = b"FORM"
GAME_MAGIC_TAG = b"GEN8"


def validate_inputs(
    ipa_path: Path,
    game_ios_path: Path,
    expected_bundle_id: str = DEFAULT_BUNDLE_ID,
    expected_version: str = DEFAULT_VERSION,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings = [
        "FORM/GEN8 não comprova compatibilidade com iOS, versão ou idioma PT-BR.",
        "O verificador não altera nem assina o IPA; trocar arquivos invalida a assinatura existente.",
    ]

    if not ipa_path.is_file():
        errors.append(f"IPA não encontrado: {ipa_path}")
    if not game_ios_path.is_file():
        errors.append(f"Arquivo candidato game.ios não encontrado: {game_ios_path}")
    if errors:
        return errors, warnings

    try:
        with zipfile.ZipFile(ipa_path) as archive:
            info_paths = [
                name for name in archive.namelist()
                if name.startswith("Payload/") and name.endswith(".app/Info.plist")
            ]
            if len(info_paths) != 1:
                errors.append("O IPA precisa conter exatamente um Payload/*.app/Info.plist.")
            else:
                info_path = info_paths[0]
                app_dir = info_path.rsplit("/", 1)[0]
                game_entry = f"{app_dir}/games/game.ios"
                if game_entry not in archive.namelist():
                    errors.append(f"Recurso iOS esperado não encontrado no IPA: {game_entry}")

                try:
                    info = plistlib.loads(archive.read(info_path))
                except (KeyError, plistlib.InvalidFileException, ValueError) as exc:
                    errors.append(f"Info.plist inválido: {exc}")
                else:
                    actual_bundle_id = info.get("CFBundleIdentifier")
                    actual_version = info.get("CFBundleShortVersionString")
                    if actual_bundle_id != expected_bundle_id:
                        errors.append(
                            f"Bundle ID diferente: esperado {expected_bundle_id}, encontrado {actual_bundle_id}."
                        )
                    if actual_version != expected_version:
                        errors.append(
                            f"Versão diferente: esperada {expected_version}, encontrada {actual_version}."
                        )
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"Não foi possível ler o IPA como arquivo ZIP: {exc}")

    try:
        with game_ios_path.open("rb") as candidate:
            header = candidate.read(12)
    except OSError as exc:
        errors.append(f"Não foi possível ler o arquivo candidato: {exc}")
    else:
        if len(header) < 12 or header[:4] != GAME_MAGIC_PREFIX or header[8:12] != GAME_MAGIC_TAG:
            errors.append("O arquivo candidato não tem o cabeçalho básico FORM/GEN8 esperado.")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica metadados básicos do IPA e um recurso candidato game.ios."
    )
    parser.add_argument("--ipa", required=True, type=Path, help="Caminho para o IPA original")
    parser.add_argument("--game-ios", required=True, type=Path, help="Caminho para o recurso candidato")
    parser.add_argument("--expected-bundle-id", default=DEFAULT_BUNDLE_ID)
    parser.add_argument("--expected-version", default=DEFAULT_VERSION)
    args = parser.parse_args()

    errors, warnings = validate_inputs(
        args.ipa, args.game_ios, args.expected_bundle_id, args.expected_version
    )
    for warning in warnings:
        print(f"AVISO: {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERRO: {error}", file=sys.stderr)
    if errors:
        return 1
    print("OK: estrutura básica e metadados conferidos; compatibilidade/localização não foram comprovadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
