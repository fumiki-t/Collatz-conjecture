import json
from pathlib import Path

import pytest

from src.phase43_search import search
from verifier import verify_phase43 as verifier


@pytest.fixture
def big():
    return json.loads(Path("artifacts/phase43_certificate_703.json").read_text())


def test_full_independent_audit():
    result=verifier.audit(Path("artifacts"))
    assert result["valid"] and not result["proves_collatz"]
    assert (result["query_count"],result["certified_no_improvement"],result["improvements"])==(2668,185,2483)
    assert (result["reference_vertices"],result["certificate_703_vertices"])==(1189,1188)
    assert result==json.loads(Path("artifacts/phase43_verifier.json").read_text())


@pytest.mark.parametrize("field,value",[("schema","wrong"),("endpoint",1257),
    ("odd_count",50),("source_bound",704),("source_bound",706),("source_bound",True),
    ("source",0),("source",-703),("source",703.0),("source",True),("length",79),
    ("length",80.0),("length",True),("proves_collatz",True),("proves_collatz",0),
    ("status","UNKNOWN"),("status","NO_HIT"),("potential",{})])
def test_metadata_tampering(big,field,value):
    big[field]=value
    assert not verifier.verify(big)


@pytest.mark.parametrize("kind",["delete_source","zero_endpoint","zero_denominator",
    "negative_value","duplicate","unsorted","noncanonical","float_value","bool_state",
    "wrong_edge","upper_envelope"])
def test_potential_tampering(big,kind):
    rows=big["potential"]
    if kind=="delete_source":
        big["potential"]=[r for r in rows if r[0]!=703]
    elif kind=="zero_endpoint":
        next(r for r in rows if r[0]==1256)[1]=0
    elif kind=="zero_denominator":
        rows[0][2]=0
    elif kind=="negative_value":
        rows[0][1]=-1
    elif kind=="duplicate":
        rows.append(rows[0])
    elif kind=="unsorted":
        rows.reverse()
    elif kind=="noncanonical":
        rows[0][1]*=2
        rows[0][2]*=2
    elif kind=="float_value":
        rows[0][1]=float(rows[0][1])
    elif kind=="bool_state":
        rows[0][0]=True
    elif kind=="wrong_edge":
        r=next(r for r in rows if r[0]==703)
        r[1]=0
    elif kind=="upper_envelope":
        # Satisfies endpoint and listed-edge inequalities, but violates the
        # envelope at 2. An omitted state 4 then breaks the global inequality.
        big=search(1,0)
        big["potential"]=[[1,1,1],[2,3,5]]
    assert not verifier.verify(big)


@pytest.mark.parametrize("kind",["wrong_source","negative_source","equal","wrong_q","bool_length"])
def test_improvement_tampering(kind):
    record=search(59,6)
    if kind=="wrong_source": record["witness"]["source"]=38
    elif kind=="negative_source": record["witness"]["source"]=-39
    elif kind=="equal": record["witness"]={"source":59,"length":6,"odd_count":4}
    elif kind=="wrong_q": record["witness"]["odd_count"]=4
    elif kind=="bool_length": record["witness"]["length"]=True
    assert not verifier.verify(record)


@pytest.mark.parametrize("budget",[{"maximum_work":1},{"maximum_candidates":10}])
def test_resource_unknown_is_never_a_certificate(budget):
    record=search(703,80,**budget)
    assert record["status"]=="UNKNOWN" and not verifier.verify(record)
    record["status"]="CERTIFIED_NO_STRICT_IMPROVEMENT"
    assert not verifier.verify(record)


@pytest.mark.parametrize("field",["rows","reciprocal_upper","coarse_upper","log2_lower",
    "log13_over8_lower","three_log13_lower","inherited_sha256","proves_collatz"])
def test_capacity_tampering(field):
    data=json.loads(Path("artifacts/phase43_capacity.json").read_text())
    if field=="rows": data[field][48][2]+=1
    elif field=="inherited_sha256": data[field][next(iter(data[field]))]="0"*64
    elif field=="proves_collatz": data[field]=True
    else: data[field][0]+=1
    with pytest.raises(verifier.VerificationError):
        verifier.capacity_check(data)


@pytest.mark.parametrize("kind",["omitted_seed","omitted_successor","extra","duplicate","float"])
def test_closed_reference_tampering(kind):
    data=json.loads(Path("artifacts/phase43_reference.json").read_text())
    if kind=="omitted_seed": data["vertices"].remove(703)
    elif kind=="omitted_successor": data["vertices"].remove(2512)
    elif kind=="extra": data["vertices"].append(10**9)
    elif kind=="duplicate": data["vertices"].append(1)
    elif kind=="float": data["vertices"][0]=1.0
    with pytest.raises(verifier.VerificationError):
        verifier.reference(data,705)


def test_no_search_diagnostics_used(big):
    # Diagnostics are explicitly not proof fields. A self-contained verifier
    # still works after every generator work statistic has been removed.
    del big["diagnostics"]
    assert verifier.verify(big)


def test_empty_and_malformed_records():
    for data in (None,[],{},False,{"schema":"collatz-phase43-normalization-barrier-v1"}):
        assert not verifier.verify(data)


def test_unknown_cli_exits_failure(tmp_path,monkeypatch,capsys):
    path=tmp_path/"unknown.json"
    path.write_text(json.dumps(search(703,80,maximum_work=1)))
    monkeypatch.setattr("sys.argv",["verify_phase43","--certificate",str(path)])
    with pytest.raises(SystemExit) as e:
        verifier.main()
    assert e.value.code==1
    assert json.loads(capsys.readouterr().out)["valid"] is False
