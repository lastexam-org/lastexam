import copy
import json
import math

import pytest
from lastexam import evaluate, grade, load_suite, public_task
from lastexam.cli import main


def test_reference_and_missing_reports():
    suite = load_suite()
    report = evaluate(suite, {t["id"]:t["reference"] for t in suite["tasks"]})
    assert report["accuracy"] == 1
    assert report["total"] == 12
    assert len(report["by_domain"]) == 6
    assert evaluate(suite,{})["accuracy"] == 0


@pytest.mark.parametrize("answer", [True,False,None,"1",float("nan"),float("inf"),[],[1],{}])
def test_malformed_numeric_answers_fail(answer):
    task = {"grader":{"type":"numeric"},"reference":1.}
    assert grade(task,answer) == 0


def test_tolerance_and_nested_shapes():
    task = {"grader":{"type":"numeric","atol":1e-5,"rtol":0},"reference":[[1.,2.]]}
    assert grade(task,[[1.000001,2]]) == 1
    assert grade(task,[[1.1,2]]) == 0
    assert grade(task,[1,2]) == 0


def test_exact_answers_are_type_strict():
    task = {"grader":{"type":"exact"},"reference":{"bits":[1,0]}}
    assert grade(task,{"bits":[True,False]}) == 0
    assert grade(task,{"bits":[1,0]}) == 1


def test_no_references_in_exports(capsys):
    task = load_suite()["tasks"][0]
    assert "reference" not in public_task(task)
    assert "reference" in task
    assert main(["export"]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(rows)==12
    assert all("reference" not in row and "reference_method" not in row for row in rows)


def test_cli_end_to_end(tmp_path,capsys):
    suite = load_suite()
    answers = tmp_path/"answers.json"
    answers.write_text(json.dumps({t["id"]:t["reference"] for t in suite["tasks"]}))
    assert main(["evaluate",str(answers)]) == 0
    assert json.loads(capsys.readouterr().out)["correct"] == 12
    assert main(["show","bad"]) == 2
    assert "Unknown task" in capsys.readouterr().err
    assert main(["list","--domain","no-such-domain"]) == 2


def test_unknown_ids_rejected():
    with pytest.raises(ValueError,match="Unknown task IDs"):
        evaluate(load_suite(),{"typo":0})
    with pytest.raises(ValueError,match="JSON object"):
        evaluate(load_suite(),[])


@pytest.mark.parametrize("mutation", ["duplicate","grader","reference","tolerance","schema","empty"])
def test_invalid_custom_suites(tmp_path,mutation):
    suite = copy.deepcopy(load_suite())
    if mutation == "duplicate": suite["tasks"].append(suite["tasks"][0])
    if mutation == "grader": suite["tasks"][0]["grader"]["type"] = "execute"
    if mutation == "reference": suite["tasks"][0]["reference"] = float("nan")
    if mutation == "tolerance": suite["tasks"][0]["grader"]["atol"] = -1
    if mutation == "schema": suite["schema_version"] = 2
    if mutation == "empty": suite["tasks"] = []
    path = tmp_path/"suite.json"; path.write_text(json.dumps(suite))
    with pytest.raises(ValueError): load_suite(path)


def test_custom_suite_loads(tmp_path):
    suite = load_suite()
    path = tmp_path/"suite.json"; path.write_text(json.dumps(suite))
    assert load_suite(path)==suite
