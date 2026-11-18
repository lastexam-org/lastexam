"""Independently check every bundled answer using alternate constructions."""
import itertools
import math

import numpy as np
import pytest
from lastexam import grade, load_suite

TASKS = {t["id"].split(".", 1)[1]: t for t in load_suite()["tasks"]}


def check(name, answer):
    # Normalize NumPy scalars to the actual JSON submission types.
    import json
    assert grade(TASKS[name], json.loads(json.dumps(answer))) == 1


def test_qpe_fourier_sum():
    amplitudes = np.array([sum(np.exp(2j*np.pi*np.arange(8)*(1/3-y/8)))/8 for y in range(8)])
    check("computing.qpe", (abs(amplitudes)**2).tolist())
    assert sum(abs(amplitudes)**2) == pytest.approx(1)


def test_grover_statevector():
    state = np.ones(128)/np.sqrt(128)
    for _ in range(5):
        state[:3] *= -1
        state = 2*np.mean(state)-state
    check("computing.grover", float(sum(state[:3]**2)))


def entropy(rho):
    vals = np.linalg.eigvalsh(rho)
    return float(-sum(v*np.log2(v) for v in vals if v > 1e-14))


def test_entropy_and_partial_transpose():
    bell = np.array([1,0,0,1])/np.sqrt(2)
    rho = .6*np.outer(bell,bell)+.4*np.eye(4)/4
    marginal = np.trace(rho.reshape(2,2,2,2), axis1=1, axis2=3)
    check("information.entropy", [entropy(rho),entropy(marginal),2*entropy(marginal)-entropy(rho)])
    singlet = np.array([0,1,-1,0])/np.sqrt(2)
    rho = .7*np.outer(singlet,singlet)+.3*np.eye(4)/4
    pt = rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    norm = float(sum(abs(np.linalg.eigvalsh(pt))))
    check("information.negativity", [(norm-1)/2,math.log2(norm)])


def test_ising_free_fermion_spectrum():
    # Open-chain Jordan-Wigner solution, independent of dense spin construction.
    coupling = .7*np.eye(4) + np.diag(np.ones(3),1)
    modes = np.linalg.svd(coupling,compute_uv=False)
    spectrum = sorted(float(np.dot(signs,modes)) for signs in itertools.product([-1,1],repeat=4))
    check("manybody.ising", spectrum)


def test_heisenberg_spin_multiplets():
    check("manybody.heisenberg", [-2.]+[-1.]*3+[0.]*7+[1.]*5)


def test_two_determinant_eigenvector():
    e,v = np.linalg.eigh([[-1.1,.18],[.18,-.4]])
    check("chemistry.subspace", [float(e[0]),float(v[1,0]**2)])


def test_hubbard_fermionic_fock_space():
    # Modes: site1 up, site1 down, site2 up, site2 down.
    basis = [s for s in range(16) if bin(s).count("1")==2]
    h = np.zeros((6,6)); d = np.zeros(6)
    for col,s in enumerate(basis):
        d[col] = int(s&3==3)+int(s&12==12)
        h[col,col] = 4*d[col]
        for a,b in [(0,2),(2,0),(1,3),(3,1)]:
            if s>>b&1 and not s>>a&1:
                sign = (-1)**(bin(s&((1<<b)-1)).count("1"))
                after = s^(1<<b)
                sign *= (-1)**(bin(after&((1<<a)-1)).count("1"))
                after |= 1<<a
                h[basis.index(after),col] -= sign
    e,v = np.linalg.eigh(h)
    check("chemistry.hubbard", [float(e[0]),float(np.dot(v[:,0]**2,d))])


def test_repetition_exhaustive_error_patterns():
    probability = sum(.13**sum(bits)*.87**(11-sum(bits))
                      for bits in itertools.product([0,1],repeat=11) if sum(bits)>5)
    check("qec.repetition", probability)


def test_steane_check_supports():
    supports = [{1,3,5,7},{2,3,6,7},{4,5,6,7}]
    check("qec.steane", [[int(3 in s) for s in supports],[int(5 in s) for s in supports]])


def test_routing_dynamic_programming_over_all_mappings():
    permutations = list(itertools.permutations(range(4)))
    def distance(a,b):
        order = [b.index(x) for x in a]
        return sum(order[i]>order[j] for i in range(4) for j in range(i+1,4))
    costs = {(0,1,2,3):0}
    for a,b in [(0,3),(0,2),(1,3),(0,1)]:
        costs = {p:min(cost+distance(q,p) for q,cost in costs.items())
                 for p in permutations if abs(p.index(a)-p.index(b))==1}
    check("compilation.routing", min(costs.values()))


def test_phase_polynomial_truth_table():
    original = [(1,1),(3,3),(7,1),(3,6),(1,7),(5,-1),(7,2)]
    canonical = [[3,1],[5,7],[7,3]]
    for x in range(8):
        phase = lambda terms: sum(a*(bin(mask&x).count("1")%2) for mask,a in terms)%8
        assert phase(original) == phase(canonical)
    check("compilation.phase", {"terms":canonical,"odd_terms":3})
