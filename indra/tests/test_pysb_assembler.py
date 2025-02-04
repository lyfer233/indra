import xml.etree.ElementTree as ET
from indra.assemblers.pysb import PysbAssembler
import indra.assemblers.pysb.assembler as pa
from indra.assemblers.pysb.assembler import Policy, Param
from indra.assemblers.pysb.preassembler import PysbPreassembler
from indra.assemblers.pysb.export import export_cm_network
from indra.assemblers.pysb.kappa_util import get_cm_cycles
from indra.statements import *
from pysb import bng, WILD, Monomer, Annotation
from pysb.testing import with_model
from nose.tools import raises


def test_pysb_assembler_complex1():
    member1 = Agent('BRAF')
    member2 = Agent('MEK1')
    stmt = Complex([member1, member2])
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 2
    assert len(model.monomers) == 2


def test_pysb_assembler_complex2():
    member1 = Agent('BRAF')
    member2 = Agent('MEK1')
    member3 = Agent('ERK1')
    stmt = Complex([member1, member2, member3])
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 6
    assert len(model.monomers) == 3


def test_pysb_assembler_complex3():
    hras = Agent('HRAS')
    member1 = Agent('BRAF', bound_conditions=[BoundCondition(hras, True)])
    member2 = Agent('MEK1')
    stmt = Complex([member1, member2])
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 2
    assert len(model.monomers) == 3


def test_pysb_assembler_complex_twostep():
    member1 = Agent('BRAF')
    member2 = Agent('MEK1')
    stmt = Complex([member1, member2])
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 2
    assert len(model.monomers) == 2


def test_pysb_assembler_complex_multiway():
    member1 = Agent('BRAF')
    member2 = Agent('MEK1')
    member3 = Agent('ERK1')
    stmt = Complex([member1, member2, member3])
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='multi_way')
    assert len(model.rules) == 2
    assert len(model.monomers) == 3


def test_pysb_assembler_actsub():
    stmt = ActiveForm(Agent('BRAF', mutations=[MutCondition('600', 'V', 'E')]),
                      'activity', True)
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 0
    assert len(model.monomers) == 1


def test_pysb_assembler_phos_noenz():
    enz = None
    sub = Agent('MEK1')
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 0
    assert len(model.monomers) == 0


def test_pysb_assembler_dephos_noenz():
    enz = None
    sub = Agent('MEK1')
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 0
    assert len(model.monomers) == 0


def test_pysb_assembler_phos1():
    enz = Agent('BRAF')
    sub = Agent('MEK1')
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_pysb_assembler_phos2():
    hras = Agent('HRAS')
    enz = Agent('BRAF', bound_conditions=[BoundCondition(hras, True)])
    sub = Agent('MEK1')
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 3


def test_pysb_assembler_phos3():
    hras = Agent('HRAS')
    erk1 = Agent('ERK1')
    enz = Agent('BRAF', bound_conditions=[BoundCondition(hras, True)])
    sub = Agent('MEK1', bound_conditions=[BoundCondition(erk1, True)])
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 4


def test_pysb_assembler_phos4():
    hras = Agent('HRAS')
    erk1 = Agent('ERK1')
    enz = Agent('BRAF', bound_conditions=[BoundCondition(hras, True)])
    sub = Agent('MEK1', bound_conditions=[BoundCondition(erk1, False)])
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 4


def test_pysb_assembler_autophos1():
    enz = Agent('MEK1')
    stmt = Autophosphorylation(enz, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 1


def test_pysb_assembler_autophos2():
    raf1 = Agent('RAF1')
    enz = Agent('MEK1', bound_conditions=[BoundCondition(raf1, True)])
    stmt = Autophosphorylation(enz, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_pysb_assembler_autophos3():
    egfr = Agent('EGFR')
    enz = Agent('EGFR', bound_conditions=[BoundCondition(egfr, True)])
    stmt = Autophosphorylation(enz, 'tyrosine')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 1


def test_pysb_assembler_transphos1():
    egfr = Agent('EGFR')
    enz = Agent('EGFR', bound_conditions=[BoundCondition(egfr, True)])
    stmt = Transphosphorylation(enz, 'tyrosine')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 1


def test_pysb_assembler_act1():
    egfr = Agent('EGFR')
    subj = Agent('GRB2', bound_conditions=[BoundCondition(egfr, True)])
    obj = Agent('SOS1')
    stmt = Activation(subj, obj)
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 3


def test_pysb_assembler_dephos1():
    phos = Agent('PP2A')
    sub = Agent('MEK1')
    stmt = Dephosphorylation(phos, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_pysb_assembler_dephos2():
    phos = Agent('PP2A')
    raf1 = Agent('RAF1')
    sub = Agent('MEK1', bound_conditions=[BoundCondition(raf1, True)])
    stmt = Dephosphorylation(phos, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 3


def test_pysb_assembler_gef1():
    gef = Agent('SOS1')
    ras = Agent('HRAS')
    stmt = Gef(gef, ras)
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_pysb_assembler_gap1():
    gap = Agent('NF1')
    ras = Agent('HRAS')
    stmt = Gap(gap, ras)
    pa = PysbAssembler([stmt])
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_pysb_assembler_actmod1():
    mek = Agent('MEK')
    erk = Agent('ERK')
    stmts = []
    mc1 = ModCondition('phosphorylation', 'serine', '218')
    mc2 = ModCondition('phosphorylation', 'serine', '222')
    stmts.append(ActiveForm(Agent('MEK', mods=[mc1, mc2]), 'activity', True))
    stmts.append(Phosphorylation(mek, erk, 'threonine', '185'))
    stmts.append(Phosphorylation(mek, erk, 'tyrosine', '187'))
    pa = PysbAssembler(stmts)
    model = pa.make_model()
    assert len(model.rules) == 2
    assert len(model.monomers) == 2
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 5


def test_pysb_assembler_actmod2():
    mek = Agent('MEK', activity=ActivityCondition('activity', True))
    erk = Agent('ERK')
    stmts = []
    stmts.append(ActiveForm(Agent(
        'MEK', mods=[ModCondition('phosphorylation', 'serine', '218')]),
        'activity', True))
    stmts.append(ActiveForm(Agent(
        'MEK', mods=[ModCondition('phosphorylation', 'serine', '222')]),
        'activity', True))
    stmts.append(Phosphorylation(mek, erk, 'threonine', '185'))
    stmts.append(Phosphorylation(mek, erk, 'tyrosine', '187'))
    pa = PysbAssembler(stmts)
    model = pa.make_model()
    assert len(model.rules) == 4
    assert len(model.monomers) == 2
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 9


def test_pysb_assembler_phos_twostep1():
    enz = Agent('BRAF')
    sub = Agent('MEK1')
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 3
    assert len(model.monomers) == 2


def test_pysb_assembler_twostep_mixed():
    member1 = Agent('BRAF')
    member2 = Agent('RAF1')
    st1 = Complex([member1, member2])
    st2 = Phosphorylation(Agent('MAP2K1'), Agent('MAPK3'))
    pa = PysbAssembler([st1, st2])
    pa.make_model(policies='two_step')
    assert len(pa.model.rules) == 5
    assert len(pa.model.monomers) == 4


def test_pysb_assembler_phos_twostep_local():
    enz = Agent('BRAF')
    sub = Agent('MEK1')
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 3
    assert len(model.monomers) == 2


def test_pysb_assembler_phos_twostep_local_to_global():
    enz = Agent('BRAF')
    sub = Agent('MEK1')
    stmt = Phosphorylation(enz, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')
    # This call should have reverted to default policy
    model = pa.make_model()
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_pysb_assembler_dephos_twostep1():
    phos = Agent('PP2A')
    sub = Agent('MEK1')
    stmt = Dephosphorylation(phos, sub, 'serine', '222')
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 3
    assert len(model.monomers) == 2


def test_statement_specific_policies():
    enz = Agent('BRAF')
    sub = Agent('MEK1')
    phos = Agent('PP2A')
    stmt1 = Phosphorylation(enz, sub, 'serine', '222')
    stmt2 = Dephosphorylation(phos, sub, 'serine', '222')
    policies = {'Phosphorylation': 'two_step',
                'Dephosphorylation': 'interactions_only'}
    pa = PysbAssembler([stmt1, stmt2])
    model = pa.make_model(policies=policies)
    assert len(model.rules) == 4
    assert len(model.monomers) == 3


def test_unspecified_statement_policies():
    enz = Agent('BRAF')
    sub = Agent('MEK1')
    phos = Agent('PP2A')
    stmt1 = Phosphorylation(enz, sub, 'serine', '222')
    stmt2 = Dephosphorylation(phos, sub, 'serine', '222')
    policies = {'Phosphorylation': 'two_step',
                'other': 'interactions_only'}
    pa = PysbAssembler([stmt1, stmt2])
    model = pa.make_model(policies=policies)
    assert len(model.rules) == 4
    assert len(model.monomers) == 3


def test_activity_activity():
    subj = Agent('KRAS')
    obj = Agent('BRAF')
    stmt = Activation(subj, obj)
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='interactions_only')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_activity_activity2():
    subj = Agent('KRAS')
    obj = Agent('BRAF')
    stmt = Activation(subj, obj)
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='one_step')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_activity_activity2():
    subj = Agent('Vemurafenib')
    obj = Agent('BRAF')
    stmt = Inhibition(subj, obj)
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='interactions_only')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_activity_activity3():
    subj = Agent('Vemurafenib')
    obj = Agent('BRAF')
    stmt = Inhibition(subj, obj)
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='one_step')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_rule_name_str_1():
    s = pa.get_agent_rule_str(Agent('BRAF'))
    assert s == 'BRAF'


def test_rule_name_str_2():
    a = Agent('GRB2',
              bound_conditions=[BoundCondition(Agent('EGFR'), True)])
    s = pa.get_agent_rule_str(a)
    assert s == 'GRB2_EGFR'


def test_rule_name_str_3():
    a = Agent('GRB2',
              bound_conditions=[BoundCondition(Agent('EGFR'), False)])
    s = pa.get_agent_rule_str(a)
    assert s == 'GRB2_nEGFR'


def test_rule_name_str_4():
    a = Agent('BRAF', mods=[ModCondition('phosphorylation', 'serine')])
    s = pa.get_agent_rule_str(a)
    assert s == 'BRAF_phosphoS'


def test_rule_name_str_5():
    a = Agent('BRAF', mods=[ModCondition('phosphorylation', 'serine', '123')])
    s = pa.get_agent_rule_str(a)
    assert s == 'BRAF_phosphoS123'


def test_neg_act_mod():
    mc = ModCondition('phosphorylation', 'serine', '123', False)
    st1 = ActiveForm(Agent('BRAF', mods=[mc]), 'activity', True)
    braf = Agent('BRAF', activity=ActivityCondition('active', True))
    st2 = Phosphorylation(braf, Agent('MAP2K2'))
    pa = PysbAssembler([st1, st2])
    pa.make_model(policies='one_step')
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'S123': ('u', WILD)}


def test_pos_agent_mod():
    mc = ModCondition('phosphorylation', 'serine', '123', True)
    st = Phosphorylation(Agent('BRAF', mods=[mc]), Agent('MAP2K2'))
    pa = PysbAssembler([st])
    pa.make_model(policies='one_step')
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'S123': ('p', WILD)}


def test_neg_agent_mod():
    mc = ModCondition('phosphorylation', 'serine', '123', False)
    st = Phosphorylation(Agent('BRAF', mods=[mc]), Agent('MAP2K2'))
    pa = PysbAssembler([st])
    pa.make_model(policies='one_step')
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'S123': ('u', WILD)}


def test_mut():
    mut = MutCondition('600', 'V', 'E')
    st = Phosphorylation(Agent('BRAF', mutations=[mut]), Agent('MEK'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'V600': 'E'}


def test_mut_missing1():
    mut = MutCondition('600', 'V', None)
    st = Phosphorylation(Agent('BRAF', mutations=[mut]), Agent('MEK'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'V600': 'X'}


def test_mut_missing2():
    mut = MutCondition('600', None, 'E')
    st = Phosphorylation(Agent('BRAF', mutations=[mut]), Agent('MEK'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'mut600': 'E'}


def test_mut_missing3():
    mut = MutCondition(None, 'V', 'E')
    st = Phosphorylation(Agent('BRAF', mutations=[mut]), Agent('MEK'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'V': 'E'}


def test_mut_missing4():
    mut = MutCondition(None, None, None)
    st = Phosphorylation(Agent('BRAF', mutations=[mut]), Agent('MEK'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.monomer.name == 'BRAF'
    assert braf.site_conditions == {'mut': 'X'}


def test_agent_loc():
    st = Phosphorylation(Agent('BRAF', location='cytoplasm'), Agent('MEK'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    braf = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert braf.site_conditions == {'loc': 'cytoplasm'}


def test_translocation():
    st = Translocation(Agent('FOXO3A'), 'nucleus', 'cytoplasm')
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    f1 = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert f1.site_conditions == {'loc': 'nucleus'}
    f2 = r.product_pattern.complex_patterns[0].monomer_patterns[0]
    assert f2.site_conditions == {'loc': 'cytoplasm'}
    assert r.rate_forward.name == 'kf_foxo3a_nucleus_cytoplasm_1'


def test_translocation_to():
    st = Translocation(Agent('FOXO3A'), None, 'nucleus')
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    f1 = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert f1.site_conditions == {'loc': 'cytoplasm'}
    f2 = r.product_pattern.complex_patterns[0].monomer_patterns[0]
    assert f2.site_conditions == {'loc': 'nucleus'}
    assert r.rate_forward.name == 'kf_foxo3a_cytoplasm_nucleus_1'


def test_phos_atpdep():
    st = Phosphorylation(Agent('BRAF'), Agent('MEK'), 'S', '222')
    pa = PysbAssembler([st])
    pa.make_model(policies='atp_dependent')
    assert len(pa.model.rules) == 5


def test_set_context():
    st = Phosphorylation(Agent('MAP2K1'), Agent('MAPK3'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert pa.model.parameters['MAP2K1_0'].value == pa.default_initial_amount
    assert pa.model.parameters['MAPK3_0'].value == pa.default_initial_amount
    pa.set_context('A375_SKIN')
    assert pa.model.parameters['MAP2K1_0'].value > 10000
    assert pa.model.parameters['MAPK3_0'].value > 10000


def test_set_context_monomer_notfound():
    st = Phosphorylation(Agent('MAP2K1'), Agent('XYZ'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert pa.model.parameters['MAP2K1_0'].value == pa.default_initial_amount
    assert pa.model.parameters['XYZ_0'].value == pa.default_initial_amount
    pa.add_default_initial_conditions(100)
    assert pa.model.parameters['MAP2K1_0'].value == 100
    assert pa.model.parameters['XYZ_0'].value == 100
    pa.set_context('A375_SKIN')
    assert pa.model.parameters['MAP2K1_0'].value > 10000
    assert pa.model.parameters['XYZ_0'].value == pa.default_initial_amount


def test_set_context_celltype_notfound():
    st = Phosphorylation(Agent('MAP2K1'), Agent('MAPK3'))
    pa = PysbAssembler([st])
    pa.make_model()
    pa.set_context('XYZ')


def test_annotation():
    st = Phosphorylation(Agent('BRAF', db_refs = {'UP': 'P15056'}),
                         Agent('MAP2K2', db_refs = {'HGNC': '6842'}))
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.annotations) == 5


def test_annotation_regamount():
    st1 = IncreaseAmount(Agent('BRAF', db_refs = {'UP': 'P15056'}),
                         Agent('MAP2K2', db_refs = {'HGNC': '6842'}))
    st2 = DecreaseAmount(Agent('BRAF', db_refs = {'UP': 'P15056'}),
                         Agent('MAP2K2', db_refs = {'HGNC': '6842'}))
    pa = PysbAssembler([st1, st2])
    pa.make_model()
    assert len(pa.model.annotations) == 8


def test_print_model():
    st = Phosphorylation(Agent('MAP2K1'), Agent('MAPK3'))
    pa = PysbAssembler([st])
    pa.make_model()
    pa.save_model('/dev/null')


def test_save_rst():
    st = Phosphorylation(Agent('MAP2K1'), Agent('MAPK3'))
    pa = PysbAssembler([st])
    pa.make_model()
    pa.save_rst('/dev/null')


def test_export_model():
    st = Phosphorylation(Agent('MAP2K1'), Agent('MAPK3'))
    pa = PysbAssembler([st])
    pa.make_model()
    exp_str = pa.export_model('kappa')
    assert exp_str
    exp_str = pa.export_model('bngl')
    assert exp_str
    exp_str = pa.export_model('sbml', file_name='/dev/null')
    assert exp_str


def test_assemble_export_sbgn():
    # Add various statements to test their assembly
    st = Phosphorylation(Agent('BRAF'), Agent('MAP2K1'))
    mc = ModCondition('phosphorylation', None, None, True)
    st2 = Activation(Agent('MAP2K1', mods=[mc]), Agent('MAPK1'))
    st3 = Complex([Agent('MAPK1'), Agent('DUSP6')])
    st4 = DecreaseAmount(None, Agent('DUSP6'))
    pa = PysbAssembler([st, st2, st3, st4])
    pa.make_model()
    # Export to SBGN
    model = pa.export_model('sbgn')
    assert model is not None
    # Test that the right elements are there in the result
    et = ET.fromstring(model)
    from indra.assemblers.sbgn.assembler import sbgn_ns
    sbgn_nss = {'s': sbgn_ns}
    glyphs = et.findall('s:map/s:glyph', namespaces=sbgn_nss)
    glyph_classes = [g.attrib.get('class') for g in glyphs]
    assert glyph_classes.count('macromolecule') == 6
    assert glyph_classes.count('complex') == 2
    assert glyph_classes.count('process') == 10
    return pa


def test_name_standardize():
    n = pa._n('.*/- ^&#@$')
    assert isinstance(n, str)
    assert n == '__________'
    n = pa._n('14-3-3')
    assert isinstance(n, str)
    assert n == 'p14_3_3'
    n = pa._n('\U0001F4A9bar')
    assert isinstance(n, str)
    assert n == 'bar'


def test_generate_equations():
    st = Phosphorylation(Agent('MAP2K1'), Agent('MAPK3'))
    pa = PysbAssembler([st])
    pa.make_model()
    bng.generate_equations(pa.model)


def test_non_python_name_phos():
    st = Phosphorylation(Agent('14-3-3'), Agent('BRAF kinase'))
    pa = PysbAssembler([st])
    pa.make_model()
    names = [m.name for m in pa.model.monomers]
    assert 'BRAF_kinase' in names
    assert 'p14_3_3' in names
    bng.generate_equations(pa.model)


def test_non_python_name_bind():
    st = Complex([Agent('14-3-3'), Agent('BRAF kinase')])
    pa = PysbAssembler([st])
    pa.make_model()
    bng.generate_equations(pa.model)


def test_decreaseamount_one_step():
    subj = Agent('KRAS')
    obj = Agent('BRAF')
    st1 = DecreaseAmount(subj, obj)
    st2 = DecreaseAmount(None, obj)
    pa = PysbAssembler([st1, st2])
    model = pa.make_model(policies='one_step')
    assert len(model.rules) == 2
    assert len(model.monomers) == 2


def test_decreaseamount_interactions_only():
    subj = Agent('KRAS')
    obj = Agent('BRAF')
    st1 = DecreaseAmount(subj, obj)
    st2 = DecreaseAmount(None, obj)
    pa = PysbAssembler([st1, st2])
    model = pa.make_model(policies='interactions_only')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_increaseamount_one_step():
    subj = Agent('KRAS')
    obj = Agent('BRAF')
    st1 = IncreaseAmount(subj, obj)
    st2 = IncreaseAmount(None, obj)
    pa = PysbAssembler([st1, st2])
    model = pa.make_model(policies='one_step')
    assert len(model.rules) == 2
    assert len(model.monomers) == 2


def test_increaseamount_interactions_only():
    subj = Agent('KRAS')
    obj = Agent('BRAF')
    st1 = IncreaseAmount(subj, obj)
    st2 = IncreaseAmount(None, obj)
    pa = PysbAssembler([st1, st2])
    model = pa.make_model(policies='interactions_only')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2


def test_missing_catalytic_default_site():
    c8 = Agent('CASP8', activity=ActivityCondition('catalytic', True))
    c3 = Agent('CASP3')
    stmt = Activation(c8, c3, 'catalytic')
    # Interactions only
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='interactions_only')
    # One step
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='one_step')
    # Two step
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')


def test_missing_transcription_default_site():
    p53 = Agent('TP53', activity=ActivityCondition('transcription', True))
    bax = Agent('BAX')
    stmt = Activation(p53, bax)
    # Interactions only
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='interactions_only')
    # One step
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='one_step')
    # Two step
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies='two_step')


def test_translocation_loc_special_char():
    st = Translocation(Agent('KSR1'), 'cytoplasm', 'cell surface')
    pa = PysbAssembler([st])
    pa.make_model()
    assert len(pa.model.rules) == 1
    r = pa.model.rules[0]
    f1 = r.reactant_pattern.complex_patterns[0].monomer_patterns[0]
    assert f1.site_conditions == {'loc': 'cytoplasm'}
    f2 = r.product_pattern.complex_patterns[0].monomer_patterns[0]
    assert f2.site_conditions == {'loc': 'cell_surface'}
    assert r.rate_forward.name == 'kf_ksr1_cytoplasm_cell_surface_1'


@with_model
def test_get_mp_with_grounding():
    foo = Agent('Foo', db_refs={'HGNC': 'foo'})
    a = Agent('A', db_refs={'HGNC': '6840'})
    b = Agent('B', db_refs={'HGNC': '6871'})
    Monomer('A_monomer')
    Monomer('B_monomer')
    Annotation(A_monomer, 'https://identifiers.org/hgnc:6840')
    Annotation(B_monomer, 'https://identifiers.org/hgnc:6871')
    mps = list(pa.grounded_monomer_patterns(model, foo))
    assert len(mps) == 0
    mps = list(pa.grounded_monomer_patterns(model, a))
    assert len(mps) == 1, mps
    assert mps[0].monomer == A_monomer
    mps = list(pa.grounded_monomer_patterns(model, b))
    assert len(mps) == 1
    assert mps[0].monomer == B_monomer


@with_model
def test_get_mp_with_grounding_2():
    a1 = Agent('A', mods=[ModCondition('phosphorylation', None, None)],
               db_refs={'HGNC': '6840'})
    a2 = Agent('A', mods=[ModCondition('phosphorylation', 'Y', '187')],
               db_refs={'HGNC': '6840'})
    Monomer('A_monomer', ['phospho', 'T185', 'Y187'],
            {'phospho': 'y', 'T185': ['u', 'p'], 'Y187': ['u', 'p']})
    Annotation(A_monomer, 'https://identifiers.org/hgnc:6840')
    A_monomer.site_annotations = [
        Annotation(('phospho', 'y'), 'phosphorylation', 'is_modification'),
        Annotation(('T185', 'p'), 'phosphorylation', 'is_modification'),
        Annotation(('Y187', 'p'), 'phosphorylation', 'is_modification'),
        Annotation('T185', 'T', 'is_residue'),
        Annotation('T185', '185', 'is_position'),
        Annotation('Y187', 'Y', 'is_residue'),
        Annotation('Y187', '187', 'is_position')
    ]
    mps_1 = list(pa.grounded_monomer_patterns(model, a1))
    assert len(mps_1) == 3
    mps_2 = list(pa.grounded_monomer_patterns(model, a2))
    assert len(mps_2) == 1
    mp = mps_2[0]
    assert mp.monomer == A_monomer
    assert mp.site_conditions == {'Y187': ('p', WILD)}
    # TODO Add test for unmodified agent!
    # TODO Add test involving multiple (possibly degenerate) modifications!
    # TODO Add test for generic double phosphorylation


def test_phospho_assemble_grounding():
    a = Agent('MEK1', db_refs={'HGNC': '6840'})
    b = Agent('ERK2', db_refs={'HGNC': '6871'})
    b_phos = Agent('Foo', mods=[ModCondition('phosphorylation', None, None)],
                   db_refs={'HGNC': '6871'})
    st1 = Phosphorylation(a, b, 'T', '185')
    # One step

    def check_policy(policy):
        pysb_asmb = pa.PysbAssembler([st1])
        model = pysb_asmb.make_model(policies=policy)
        mps = list(pa.grounded_monomer_patterns(model, b_phos))
        assert len(mps) == 1
        assert mps[0].monomer.name == 'ERK2'
        assert mps[0].site_conditions == {'T185': ('p', WILD)}
    for policy in ('one_step', 'interactions_only', 'two_step',
                   'atp_dependent'):
        check_policy(policy)


def test_get_grounded_agents_from_model():
    mek = Agent('MEK1', db_refs={'HGNC': '6840'})
    erk = Agent('ERK2', db_refs={'HGNC': '6871'})
    erk_phos = Agent('ERK2', db_refs={'HGNC': '6871'},
                     mods=[ModCondition('phosphorylation')])
    erk_phos_y187 = Agent('ERK2', db_refs={'HGNC': '6871'},
                       mods=[ModCondition('phosphorylation', 'Y', '187')])
    phos_stmt = Phosphorylation(mek, erk)
    phos_y187_stmt = Phosphorylation(mek, erk, 'Y', '187')
    pysba = pa.PysbAssembler([phos_stmt, phos_y187_stmt])
    pysb_model = pysba.make_model()
    agents_by_mp, mps_by_rule = pa.get_grounded_agents(pysb_model)
    assert isinstance(agents_by_mp, dict)
    assert isinstance(mps_by_rule, dict)
    model_agents = agents_by_mp.values()
    model_keys = set([ag.matches_key() for ag in model_agents])
    # TODO add other types of agent conditions here
    # TODO do we expect a different agent for af?
    test_keys = set([mek.matches_key(), erk_phos.matches_key(),
                     erk_phos_y187.matches_key()])
    assert len(model_keys.intersection(test_keys)) == 3


def test_phospho_mod_grounding():
    a = Agent('MEK1', mods=[ModCondition('phosphorylation', 'S', '218'),
                            ModCondition('phosphorylation', 'S', '222')],
              db_refs={'HGNC': '6840'})
    b = Agent('ERK2', db_refs={'HGNC': '6871'})
    a_phos = Agent('Foo', mods=[ModCondition('phosphorylation', None, None)],
                   db_refs={'HGNC': '6840'})
    st1 = Phosphorylation(a, b, 'T', '185')
    pysb_asmb = pa.PysbAssembler([st1])
    model = pysb_asmb.make_model(policies='one_step')
    mps = list(pa.grounded_monomer_patterns(model, a_phos))
    assert len(mps) == 2
    assert mps[0].monomer.name == 'MEK1'
    assert mps[1].monomer.name == 'MEK1'
    sc = [mp.site_conditions for mp in mps]
    assert {'S218': ('p', WILD)} in sc
    assert {'S222': ('p', WILD)} in sc
    # Check if we get the doubly phosphorylated MonomerPattern
    mps = list(pa.grounded_monomer_patterns(model, a))
    assert len(mps) == 1
    assert mps[0].monomer.name == 'MEK1'
    assert mps[0].site_conditions == {'S218': ('p', WILD),
                                      'S222': ('p', WILD)}


def test_multiple_grounding_mods():
    mek = Agent('MEK1', db_refs={'HGNC': '6840'})
    erk = Agent('ERK2', db_refs={'HGNC': '6871'})
    cbl = Agent('CBL', db_refs={'HGNC': '1541'})
    ub_phos_erk = Agent(
        'ERK2',
        mods=[ModCondition('phosphorylation', None, None),
              ModCondition('ubiquitination', None, None)],
        db_refs={'HGNC': '6871'})
    st1 = Phosphorylation(mek, erk, 'T', '185')
    st2 = Phosphorylation(mek, erk, 'Y', '187')
    st3 = Ubiquitination(cbl, erk, 'K', '40')
    st4 = Ubiquitination(cbl, erk, 'K', '50')
    pysb_asmb = pa.PysbAssembler([st1, st2, st3, st4])
    model = pysb_asmb.make_model(policies='one_step')
    mps = list(pa.grounded_monomer_patterns(model, ub_phos_erk))
    assert len(mps) == 4
    assert mps[0].monomer.name == 'ERK2'
    assert mps[1].monomer.name == 'ERK2'
    assert mps[2].monomer.name == 'ERK2'
    assert mps[3].monomer.name == 'ERK2'


def test_grounded_active_pattern():
    a = Agent('A', db_refs={'HGNC': '1234'})
    b = Agent('B', db_refs={'HGNC': '5678'})
    b_phos = Agent('B', mods=[ModCondition('phosphorylation', 'S', '100')],
                   db_refs={'HGNC': '5678'})
    b_act = Agent('B', activity=ActivityCondition('activity', True),
                  db_refs={'HGNC': '5678'})
    st1 = Phosphorylation(a, b, 'S', '100')
    st2 = ActiveForm(b_phos, 'activity', True)
    pysba = PysbAssembler([st1, st2])
    model = pysba.make_model(policies='one_step')
    mps = list(pa.grounded_monomer_patterns(model, b_act))


def _check_mod_assembly(mod_class):
    subj = Agent('KRAS')
    obj = Agent('BRAF')
    st1 = mod_class(subj, obj)

    pa = PysbAssembler([st1])
    model = pa.make_model(policies='interactions_only')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2

    pa = PysbAssembler([st1])
    model = pa.make_model(policies='one_step')
    assert len(model.rules) == 1
    assert len(model.monomers) == 2

    pa = PysbAssembler([st1])
    model = pa.make_model(policies='two_step')
    assert len(model.rules) == 3
    assert len(model.monomers) == 2


def test_modification_assembly():
    classes = AddModification.__subclasses__() + \
              RemoveModification.__subclasses__()
    for mod_class in classes:
        _check_mod_assembly(mod_class)


def test_rule_annotation():
    a = Agent('A', db_refs={'HGNC': '1234'})
    b = Agent('B', db_refs={'HGNC': '5678'})

    def check_rule_annotation(stmt, policy):
        pa = PysbAssembler([stmt])
        model = pa.make_model(policies=policy)
        subj = [ann.object for ann in model.annotations
                if ann.predicate == 'rule_has_subject']
        obj = [ann.object for ann in model.annotations
               if ann.predicate == 'rule_has_object']
        assert len(subj) == 1
        assert subj[0] == 'A'
        assert len(obj) == 1
        assert obj[0] == 'B'

    classes = AddModification.__subclasses__() + \
        RemoveModification.__subclasses__()
    for mod_class in classes:
        stmt = mod_class(a, b)
        check_rule_annotation(stmt, 'one_step')
        check_rule_annotation(stmt, 'two_step')

    # Check ATP dependent phosphorylation
    stmt = Phosphorylation(a, b)
    check_rule_annotation(stmt, 'atp_dependent')
    stmt = Activation(a, b)
    check_rule_annotation(stmt, 'one_step')
    #Skip Autophosphorylation and Transphosphorylation for now
    #Gef
    #Gap


def test_activeform_site():
    a = Agent('A', db_refs={'HGNC': '1234'})
    b = Agent('B', db_refs={'HGNC': '5678'})
    b_phos = Agent('B', mods=[ModCondition('phosphorylation', 'Y', '200')],
                   db_refs={'HGNC': '5678'})
    st1 = Phosphorylation(a, b, 'S', '100')
    st2 = ActiveForm(b_phos, 'kinase', True)
    pa = PysbAssembler([st1, st2])
    model = pa.make_model(policies='one_step')

# TODO Do the same for mutation condition
# TODO Localization condition
# TODO Bound condition
# TODO Unphosphorylated/unmodified forms (try ubiquitinated/acetylated lysine)


def test_activation_subj1():
    """No subject activity is defined."""
    st = Activation(Agent('a'), Agent('b'))
    pa = PysbAssembler([st])
    pa.make_model()
    assert pa.model.monomers['a'].sites == []
    left = pa.model.rules[0].reactant_pattern
    subj_left = left.complex_patterns[0].monomer_patterns[0]
    right = pa.model.rules[0].product_pattern
    subj_right = right.complex_patterns[0].monomer_patterns[0]
    assert subj_left.site_conditions == {}
    assert subj_right.site_conditions == {}


def test_activation_subj2():
    """Subject activity is defined explicitly."""
    a_act = Agent('a', activity=ActivityCondition('activity', True))
    st = Activation(a_act, Agent('b'))
    st2 = ActiveForm(Agent('a', mods=[ModCondition('phosphorylation')]),
                     'activity', True)
    pa = PysbAssembler([st, st2])
    pa.make_model()
    assert pa.model.monomers['a'].sites == ['phospho']
    left = pa.model.rules[0].reactant_pattern
    subj_left = left.complex_patterns[0].monomer_patterns[0]
    right = pa.model.rules[0].product_pattern
    subj_right = right.complex_patterns[0].monomer_patterns[0]
    assert subj_left.site_conditions == {u'phospho': (u'p', WILD)}
    assert subj_right.site_conditions == {u'phospho': (u'p', WILD)}


def test_activation_subj3():
    """Subject activity is defined implicitly by another statement."""
    a_act = Agent('a', activity=ActivityCondition('activity', True))
    st = Activation(a_act, Agent('b'))
    st2 = Activation(Agent('c'), Agent('a'))
    pa = PysbAssembler([st, st2])
    pa.make_model()
    assert len(pa.model.rules) == 2
    assert pa.model.monomers['a'].sites == ['activity']
    left = pa.model.rules[0].reactant_pattern
    subj_left = left.complex_patterns[0].monomer_patterns[0]
    right = pa.model.rules[0].product_pattern
    subj_right = right.complex_patterns[0].monomer_patterns[0]
    assert subj_left.site_conditions == {u'activity': (u'active')}
    assert subj_right.site_conditions == {u'activity': (u'active')}


def test_activation_subj4():
    """Subject activity is defined both explicitly and implicitly."""
    a_act = Agent('a', activity=ActivityCondition('activity', True))
    st = Activation(a_act, Agent('b'))
    st2 = Activation(Agent('c'), Agent('a'))
    st3 = ActiveForm(Agent('a', mods=[ModCondition('phosphorylation')]),
                     'activity', True)
    pa = PysbAssembler([st, st2, st3])
    pa.make_model()
    assert set(pa.model.monomers['a'].sites) == set(['activity', 'phospho'])
    left = pa.model.rules[0].reactant_pattern
    subj_left = left.complex_patterns[0].monomer_patterns[0]
    right = pa.model.rules[0].product_pattern
    subj_right = right.complex_patterns[0].monomer_patterns[0]
    assert subj_left.site_conditions == {u'phospho': (u'p', WILD)}
    assert subj_right.site_conditions == {u'phospho': (u'p', WILD)}


def test_pysb_preassembler_replace_activities1():
    st1 = ActiveForm(Agent('a', location='nucleus'), 'activity', True)
    st2 = Phosphorylation(Agent('a',
                                activity=ActivityCondition('activity', True)),
                          Agent('b'))
    ppa = PysbPreassembler([st1, st2])
    ppa.replace_activities()
    assert len(ppa.statements) == 2
    assert ppa.statements[1].enz.location == 'nucleus'


def test_pysb_preassembler_replace_activities2():
    a_act = Agent('a', activity=ActivityCondition('activity', True))
    st = Activation(a_act, Agent('b'))
    st2 = Activation(Agent('c'), Agent('a'))
    ppa = PysbPreassembler([st, st2])
    ppa.replace_activities()
    assert len(ppa.statements) == 2


def test_pysb_preassembler_replace_activities3():
    p = Agent('PPP2CA')
    bc = BoundCondition(p, False)
    erk = Agent('ERK')
    mek1 = Agent('MEK', mods=[ModCondition('phosphorylation',
                                           None, None, True)])
    mek2 = Agent('MEK', activity=ActivityCondition('activity', True),
                 bound_conditions=[bc])
    st2 = ActiveForm(mek1, 'activity', True)
    st1 = Phosphorylation(mek2, erk)
    ppa = PysbPreassembler([st1, st2])
    ppa.replace_activities()
    assert len(ppa.statements) == 2
    assert ppa.statements[0].enz.mods
    assert ppa.statements[0].enz.bound_conditions


def test_phos_michaelis_menten():
    stmt = Phosphorylation(Agent('MEK'), Agent('ERK'))
    pa = PysbAssembler([stmt])
    pa.make_model(policies='michaelis_menten')
    assert len(pa.model.parameters) == 4


def test_deubiq_michaelis_menten():
    stmt = Deubiquitination(Agent('MEK'), Agent('ERK'))
    pa = PysbAssembler([stmt])
    pa.make_model(policies='michaelis_menten')
    assert len(pa.model.parameters) == 4


def test_act_michaelis_menten():
    stmt = Activation(Agent('MEK'), Agent('ERK'))
    stmt2 = Inhibition(Agent('DUSP'), Agent('ERK'))
    pa = PysbAssembler([stmt, stmt2])
    pa.make_model(policies='michaelis_menten')
    assert len(pa.model.parameters) == 7


def test_increaseamount_hill():
    stmt = IncreaseAmount(Agent('TP53'), Agent('MDM2'))
    pa = PysbAssembler([stmt])
    pa.make_model(policies='hill')
    pa.save_model()
    assert len(pa.model.parameters) == 5


def test_convert_nosubj():
    stmt = Conversion(None, [Agent('PIP2')], [Agent('PIP3')])
    pa = PysbAssembler([stmt])
    pa.make_model()
    assert len(pa.model.parameters) == 3
    assert len(pa.model.rules) == 1
    assert len(pa.model.monomers) == 2
    # We need to make sure that these are Kappa-compatible, and the easiest
    # way to do that is by making a ModelChecker and getting the IM without
    # error
    from indra.explanation.model_checker import PysbModelChecker
    pmc = PysbModelChecker(pa.model)
    pmc.get_im()


def test_convert_subj():
    stmt = Conversion(Agent('PIK3CA'), [Agent('PIP2')], [Agent('PIP3')])
    pa = PysbAssembler([stmt])
    pa.make_model()
    assert len(pa.model.parameters) == 4
    assert len(pa.model.rules) == 1
    assert len(pa.model.monomers) == 3
    # We need to make sure that these are Kappa-compatible, and the easiest
    # way to do that is by making a ModelChecker and getting the IM without
    # error
    from indra.explanation.model_checker import PysbModelChecker
    pmc = PysbModelChecker(pa.model)
    pmc.get_im()


def test_activity_agent_rule_name():
    stmt = Phosphorylation(Agent('BRAF',
                                 activity=ActivityCondition('kinase',
                                                            True)),
                           Agent('MAP2K1',
                                 activity=ActivityCondition('activity',
                                                            False)))
    pa = PysbAssembler([stmt])
    pa.make_model()
    assert pa.model.rules[0].name == \
        'BRAF_kin_phosphorylation_MAP2K1_act_inact_phospho', \
        pa.model.rules[0].name


def test_policy_object():
    stmt = Phosphorylation(Agent('a'), Agent('b'))
    pa = PysbAssembler([stmt])
    pol = Policy('two_step')
    model = pa.make_model(policies={stmt.uuid: pol})
    assert len(model.rules) == 3
    assert str(pol) == 'Policy(two_step)'


def test_policy_parameters():
    pol = Policy('two_step', parameters={'kf': Param('a', 1.0),
                                         'kr': Param('b', 2.0),
                                         'kc': Param('c', 3.0)})
    # Make sure we can correctly stringify here
    assert str(pol)
    stmt = Deubiquitination(Agent('a'), Agent('b'))
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies={stmt.uuid: pol})
    assert model.parameters['c'].value == 3.0


@raises(pa.UnknownPolicyError)
def test_policy_object_invalid():
    stmt = Phosphorylation(Agent('a'), Agent('b'))
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies={'xyz': Policy('two_step')})
    assert len(model.rules) == 3


def test_mod_parameter():
    stmt = Phosphorylation(Agent('a'), Agent('b'))
    pol = Policy('one_step', parameters={'kf': Param('my_kf_param', 0.99)})
    pa = PysbAssembler([stmt])
    model = pa.make_model(policies={stmt.uuid: pol})
    assert model.parameters['my_kf_param'].value == 0.99


def test_policy_multiple():
    pol1 = Policy('michaelis_menten', parameters={'Km': Param('my_Km', 1.0),
                                                  'kc': Param('my_kc', 1e-1)})
    pol2 = Policy('one_step', parameters={'kf': Param('d', 10.0)})
    stmt1 = Inhibition(Agent('a'), Agent('b'))
    stmt2 = Translocation(Agent('a'), 'cytoplasm', 'nucleus')
    pa = PysbAssembler([stmt1, stmt2])
    model = pa.make_model(policies={stmt1.uuid: pol1,
                                    stmt2.uuid: pol2})
    assert model.parameters['d'].value == 10.0
    print(model.expressions['a_deactivates_b_activity_rate'])
    print(model.rules)


def test_kappa_im_export():
    stmts = [Activation(Agent('a'), Agent('b')),
             Activation(Agent('b',
                              activity=ActivityCondition('activity', True)),
                        Agent('c'))]
    pa = PysbAssembler(stmts)
    pa.make_model()
    graph = pa.export_model('kappa_im', '/dev/null')
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1


def test_kappa_cm_export():
    stmts = [Complex([Agent('a'), Agent('b')])]
    pa = PysbAssembler(stmts)
    pa.make_model()
    graph = pa.export_model('kappa_cm', '/dev/null')
    assert len(graph.nodes()) == 2
    assert len(graph.edges()) == 1


def test_contact_map_cycles_1():
    stmts = [Complex([Agent('a'), Agent('b')]),
             Complex([Agent('a'), Agent('c')]),
             Complex([Agent('b'), Agent('c')])]
    pa = PysbAssembler(stmts)
    pa.make_model()
    graph = export_cm_network(pa.model)
    assert len(graph.nodes()) == 9, len(graph.nodes)
    assert len(graph.edges()) == 9, len(graph.edges)

    cycles = get_cm_cycles(graph)
    assert len(cycles) == 1, cycles
    assert cycles[0] == ['a(b)', 'b(a)', 'b(c)', 'c(b)', 'c(a)', 'a(c)']


def test_contact_map_cycles_2():
    erk1 = Agent('MAPK1', db_refs={'HGNC': '6871'})
    erk2 = Agent('MAPK3', db_refs={'HGNC': '6877'})
    # In this case there will be no cycles because the binding site on x
    # for ERK1 and ERK2 is generated to be competitive.
    stmts = [Complex([Agent('x'), erk1]),
             Complex([Agent('x'), erk2]),
             Complex([erk1, erk2])]
    pa = PysbAssembler(stmts)
    pa.make_model()
    graph = export_cm_network(pa.model)
    assert len(graph.nodes()) == 8, len(graph.nodes)
    assert len(graph.edges()) == 8, len(graph.edges)

    cycles = get_cm_cycles(graph)
    assert not cycles, cycles
