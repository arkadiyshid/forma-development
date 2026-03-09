import requests
import json
from parse_curl import parse_curl_file


def update_cad_number(payload, new_cad):
    """
    Меняет кадастровый номер в scenarioDto.applicantAnswers
    """

    try:
        answers = payload["scenarioDto"]["applicantAnswers"]

        # Основное поле ввода
        if "c_cadNumInput" in answers:
            answers["c_cadNumInput"]["value"] = new_cad

        # Если уже есть блок cadNumber с JSON-строкой — обновляем и его
        if "cadNumber" in answers and "value" in answers["cadNumber"]:
            try:
                cad_data = json.loads(answers["cadNumber"]["value"])
                if "response" in cad_data:
                    items = cad_data["response"].get("items", [])
                    if items:
                        # меняем внутри attributes
                        for attr in items[0].get("attributes", []):
                            if attr.get("name") == "realestates_cad_number":
                                attr["value"]["value"] = new_cad
                                attr["value"]["asString"] = new_cad
                                attr["valueAsOfType"] = new_cad

                        # меняем внутри attributeValues
                        if "attributeValues" in items[0]:
                            items[0]["attributeValues"]["realestates_cad_number"] = new_cad

                answers["cadNumber"]["value"] = json.dumps(cad_data, ensure_ascii=False)

            except Exception:
                pass

    except KeyError:
        pass

    return payload

if __name__ == "__main__":
    NEW_CAD = "77:01:0002009:4306"
    config = parse_curl_file("curl.txt")
    payload = config["json"]
    if isinstance(payload, str):
        payload = json.loads(payload)
    updated_payload = update_cad_number(payload, NEW_CAD)

    # ВАШ СЕРТИФИКАТ (CRT-файл)
    MY_CA_CERT = r"C:\Users\shidlovskiyaf\combined_ca.pem" # имя твоего сертификата

    print("Запрашиваем с verify =", MY_CA_CERT)
    response = requests.request(
        method=config["method"],
        url=config["url"],
        headers=config["headers"],
        cookies=config["cookies"],
        json=updated_payload,
        verify=MY_CA_CERT # вот где используется твой сертификат!
    )

    print(response.status_code)
    print(response.text)