from ortools.sat.python import cp_model
import streamlit as st

def scale_int(value, scale=100):
    # Help function to scale float to int for CP-SAT
    return int(round(value * scale))

def minimize_production_capacity(e_f, i_bf, F, K_f, H_f, B, P_b, A_b, T, scale=100):
    # Scale parameters to ensure integers for CP-SAT solver
    int_H_f = [scale_int(H_f[f], scale) for f in range(F)]
    int_P_b = [scale_int(P_b[b], scale) for b in range(B)]
    int_T = scale_int(T, scale)
    
    # Model
    model = cp_model.CpModel()

    # Variables
    d_f = [model.NewBoolVar(f'd_{f}') for f in range(F)] # Boolean indicating if facility f is destroyed

    # Constraints
    for f in range(F):
        model.Add(
            d_f[f] <= e_f[f] # Cannot destroy facilities that are not established
        )
    
    int_N_f = [sum(int_P_b[b] * A_b[b] * i_bf[b][f] for b in range(B)) for f in range(F)]
    int_effector_cost_f = [int_H_f[f] + int_N_f[f] for f in range(F)]
    model.Add(
        sum(int_effector_cost_f[f] * d_f[f] for f in range(F)) <= int_T # Red budget constraint
    )

    # Objective
    model.Minimize(
        sum(K_f[f] * e_f[f] * (1 - d_f[f]) for f in range(F)) # Minimize total production capacity
    )

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, None, None
    
    destroyed_f = [bool(solver.Value(d_f[f])) for f in range(F)]
    N_f = [sum(P_b[b] * A_b[b] * i_bf[b][f] for b in range(B)) for f in range(F)]
    effector_cost_f = [float((H_f[f] + N_f[f]) * destroyed_f[f]) for f in range(F)]
    production_capacity = int(solver.ObjectiveValue())
    return destroyed_f, effector_cost_f, production_capacity

def maximize_remaining_production_capacity(
        F, type_f, K_f, H_f, C_f, beta_f, B, C_b, P_b, A_b, OE, T, R,
        scenarios, with_tie_breakers=True, scale=100
    ):
    # Scale parameters to ensure integers for CP-SAT solver
    int_H_f = [scale_int(H_f[f], scale) for f in range(F)]
    int_C_f = [scale_int(C_f[f], scale) for f in range(F)]
    int_C_b = [scale_int(C_b[b], scale) for b in range(B)]
    int_P_b = [scale_int(P_b[b], scale) for b in range(B)]
    int_OE = scale_int(OE, scale)
    int_T = scale_int(T, scale)

    # Model
    model = cp_model.CpModel()

    # Variables
    K_tot_star = model.NewIntVar(0, sum(K_f), 'K_tot_star') # Total remaining production capacity after worst possible attack
    e_f = [model.NewBoolVar(f'e_{f}') for f in range(F)] # Boolean variable indicating if facility f is established
    i_bf = [[model.NewBoolVar(f'i_{b}_{f}') for f in range(F)] for b in range(B)] # Boolean variable indicating if protection measure b is implemented at facility f

    # Constraints
    int_N_f = [sum(int_P_b[b] * A_b[b] * i_bf[b][f] for b in range(B)) for f in range(F)]
    int_effector_cost_f = [int_H_f[f] + int_N_f[f] for f in range(F)]
    if not scenarios:
        scenarios = [[0] * F] # Default attack scenario where no facilities are destroyed
    for s, d_f_s in enumerate(scenarios):
        phi_s = model.NewBoolVar(f'phi_{s}') # Boolean variable indicating if scenario s is feasible with the current protection measures
        model.Add(
            sum(int_effector_cost_f[f] * d_f_s[f] for f in range(F)) <= int_T
        ).OnlyEnforceIf(phi_s) # Ensures that phi_s is set to 0 if scenario s is infeasible
        model.Add(
            sum(int_effector_cost_f[f] * d_f_s[f] for f in range(F)) >= int_T + 1
        ).OnlyEnforceIf(phi_s.Not()) # Ensures that phi_s is set to 1 if scenario s is feasible
        model.Add(
            K_tot_star <= sum(K_f[f] * e_f[f] * (1 - d_f_s[f]) for f in range(F))
        ).OnlyEnforceIf(phi_s) # Remaining production capacity after attack scenario s

    for f in range(F):
        model.Add(
            sum(i_bf[b][f] for b in range(B)) <= e_f[f]
        ) # Protection measures can only be implemented at established facilities, and at most one measure at each facility
    
    int_facility_cost_f = [int_C_f[f] * e_f[f] for f in range(F)]
    int_protection_measure_cost_f = [sum(int_C_b[b] * i_bf[b][f] for b in range(B)) for f in range(F)]
    model.Add(
        sum(int_facility_cost_f[f] + int_protection_measure_cost_f[f] for f in range(F)) <= int_OE
    ) # Blue budget constraint

    for f in range(F):
        model.Add(
            sum(K_f[f] * e_f[f] * beta_f[f] for f in range(F)) <= R
        ) # Bio budget constraint

    # Symmetry breaking
    type_f_prev = type_f[0]
    for f in range(1, F):
        if type_f[f] != type_f_prev:
            type_f_prev = type_f[f]
            continue
        model.Add(
            e_f[f] <= e_f[f - 1]
        ) # Establish facilities of the same type in order
        model.Add(
            sum(i_bf[b][f] for b in range(B)) <= sum(i_bf[b][f - 1] for b in range(B))
        ) # Implement protection measures at facilities of the same type in order

    # Objective
    model.Maximize(
        K_tot_star # Maximize remaining production capacity after worst possible attack
    )

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, None, None, status
    
    if with_tie_breakers:
        # First tie-breaker
        optimal_K_tot_star = solver.Value(K_tot_star)
        model.Add(
            K_tot_star == optimal_K_tot_star
            ) # Fix K_tot_star to optimal value found
        model.Minimize(
            sum(int_protection_measure_cost_f[f] for f in range(F))
        ) # Minimize total cost of protection measures as first tie-breaker
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None, None, None, status

        # Second tie-breaker
        int_total_protection_measure_cost = sum(int_protection_measure_cost_f[f] for f in range(F))
        optimal_int_total_protection_measure_cost = solver.Value(int_total_protection_measure_cost)
        model.Add(
            int_total_protection_measure_cost == optimal_int_total_protection_measure_cost
        ) # Fix total cost of protection measures to optimal value found
        model.Maximize(
            sum(K_f[f] * e_f[f] for f in range(F))
        ) # Maximize total established production capacity as second tie-breaker
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None, None, None, status

    established_f = [bool(solver.Value(e_f[f])) for f in range(F)]
    implemented_bf = [[bool(solver.Value(i_bf[b][f])) for f in range(F)] for b in range(B)]
    remaining_production_capacity = int(solver.Value(K_tot_star))
    return established_f, implemented_bf, remaining_production_capacity, status

def solve_interdiction(F, type_f, K_f, H_f, C_f, beta_f, B, C_b, P_b, A_b, OE, T, R,
                       max_iters=200, iteration_placeholder=None, iteration_detail=None,
                       with_tie_breakers=True, scale=100):
    scenarios = [] # List of attack scenarios
    history = [] # Iteration history, for debugging
    for it in range(max_iters):
        if iteration_placeholder:
            if iteration_detail:
                iteration_placeholder.markdown(f":red-badge[{iteration_detail} :material/arrow_forward: Iterasjon: {it}]")
            else:
                iteration_placeholder.markdown(f":red-badge[Iterasjon: {it}]")
        e_f, i_bf, K_tot_star, status = maximize_remaining_production_capacity(
            F, type_f, K_f, H_f, C_f, beta_f, B, C_b, P_b, A_b, OE, T, R,
            scenarios, with_tie_breakers=with_tie_breakers, scale=scale
        )
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {"status": "INFEASABLE", "history": history}
        d_f, effector_cost_f, production_capacity = minimize_production_capacity(e_f, i_bf, F, K_f, H_f, B, P_b, A_b, T, scale=scale)
        if d_f is None:
            return {"status": "SUBPROBLEM_INFEASABLE", "history": history}
        K_tot_gap = K_tot_star - production_capacity
        # If K_tot_star > production_capacity, a worse attack scenario has been found and K_tot_star needs to be recomputed
        history.append({
            "iteration": it,
            "established_facilities": e_f,
            "implemented_protection_measures": i_bf,
            "destroyed_facilities": d_f,
            "effector_costs": effector_cost_f,
            "remaining_production_capacity_after_attack": production_capacity,
            "previous_remaining_production_capacity": K_tot_star,
            "optimality_gap": K_tot_gap
        })
        if K_tot_gap <= 0:
            return {
                "status": "OPTIMAL",
                "established_facilities": e_f,
                "implemented_protection_measures": i_bf,
                "destroyed_facilities": d_f,
                "effector_costs": effector_cost_f,
                "remaining_production_capacity_after_attack": production_capacity,
                "optimality_gap": K_tot_gap,
                "history": history
            }
        scenarios.append(d_f) # Add new attack scenario and repeat
    return {"status": "MAX_ITERS_EXCEEDED", "history": history}