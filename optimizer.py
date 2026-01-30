from ortools.sat.python import cp_model
import streamlit as st

def scale_int(value, scale=100):
    # Help function to scale float to int for CP-SAT
    return int(round(value * scale))

def minimize_production_capacity(P_A, B_R, F, K_f, e_f, H_f, a_f):
    # Model
    model = cp_model.CpModel()

    # Variables
    d_f = [model.NewBoolVar(f'd_{f}') for f in range(F)] # Boolean indicating if facility f is destroyed

    # Constraints
    for f in range(F):
        model.Add(
            d_f[f] <= e_f[f] # Cannot destroy facilities that are not established
        )
    
    scaled_missile_cost_f = [scale_int(H_f[f] + P_A * a_f[f]) for f in range(F)]
    scaled_missile_budget = scale_int(B_R)
    model.Add(
        sum(scaled_missile_cost_f[f] * d_f[f] for f in range(F)) <= scaled_missile_budget # Missile budget constraint
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
    missile_cost_f = [float((H_f[f] + P_A * a_f[f]) * destroyed_f[f]) for f in range(F)]
    production_capacity = int(solver.ObjectiveValue())
    return destroyed_f, missile_cost_f, production_capacity

def maximize_remaining_production_capacity(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                           scenarios, with_tie_breakers=True):
    # Model
    model = cp_model.CpModel()

    # Variables
    K_tot_star = model.NewIntVar(0, sum(K_f), 'K_tot_star')  # Total remaining production capacity after worst possible attack
    e_f = [model.NewBoolVar(f'e_{f}') for f in range(F)]  # Boolean variable indicating if facility f is established
    a_f = [model.NewIntVar(0, A_max, f'a_{f}') for f in range(F)]  # Number of air defense missiles protecting facility f

    # Constraints
    scaled_missile_cost_f = [scale_int(H_f[f]) + scale_int(P_A) * a_f[f] for f in range(F)]
    scaled_B_R = scale_int(B_R)
    if not scenarios:
        scenarios = [[0] * F]  # Default attack scenario where no facilities are destroyed
    for s, d_f_s in enumerate(scenarios):
        phi_s = model.NewBoolVar(f'phi_{s}')  # Boolean variable indicating if scenario s is feasible with the current air defense configuration
        model.Add(
            sum(scaled_missile_cost_f[f] * d_f_s[f] for f in range(F)) <= scaled_B_R
        ).OnlyEnforceIf(phi_s) # Ensures that phi_s is set to 0 if scenario s is infeasible
        model.Add(
            sum(scaled_missile_cost_f[f] * d_f_s[f] for f in range(F)) >= scaled_B_R + 1
        ).OnlyEnforceIf(phi_s.Not()) # Ensures that phi_s is set to 1 if scenario s is feasible
        model.Add(
            K_tot_star <= sum(K_f[f] * e_f[f] * (1 - d_f_s[f]) for f in range(F)) # Remaining production capacity after attack scenario s
        ).OnlyEnforceIf(phi_s)

    for f in range(F):
        model.Add(
            a_f[f] <= A_max * e_f[f]  # Air defense missiles can only be assigned to established facilities
        )
    
    model.Add(
        sum(C_f[f] * e_f[f] + C_A * a_f[f] for f in range(F)) <= B_B  # Facility and air defense budget constraint
    )

    type_f_prev = type_f[0]
    for f in range(1, F):
        if type_f[f] != type_f_prev:
            type_f_prev = type_f[f]
            continue
        model.Add(
            e_f[f] <= e_f[f - 1]  # Symmetry breaking: establish facilities of the same type in order
        )
        model.Add(
            a_f[f] <= a_f[f - 1]  # Symmetry breaking: assign air defense missiles in order
        )

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
        # Tie-breaker
        optimal_K_tot_star = solver.Value(K_tot_star)
        model.Add(
            K_tot_star == optimal_K_tot_star
            ) # Fix K_tot_star to optimal value found
        model.Minimize(
            sum(a_f[f] for f in range(F))
        ) # Minimize total number of air defense missiles as tie-breaker
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None, None, None, status

        # Second tie-breaker
        optimal_total_air_defense = sum(solver.Value(a_f[f]) for f in range(F))
        model.Add(
            sum(a_f[f] for f in range(F)) == optimal_total_air_defense
        ) # Fix total number of air defense missiles to optimal value found
        model.Maximize(
            sum(K_f[f] * e_f[f] for f in range(F))
        ) # Maximize total established production capacity as second tie-breaker
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None, None, None, status

    estblished_f = [bool(solver.Value(e_f[f])) for f in range(F)]
    air_defense_f = [int(solver.Value(a_f[f])) for f in range(F)]
    remaining_production_capacity = int(solver.Value(K_tot_star))
    return estblished_f, air_defense_f, remaining_production_capacity, status

def solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                       max_iters=1000, iteration_placeholder=None, iteration_detail=None,
                       with_tie_breakers=True):
    scenarios = [] # List of attack scenarios
    history = [] # Iteration history
    for it in range(max_iters):
        if iteration_placeholder:
            if iteration_detail:
                iteration_placeholder.markdown(f":red-badge[{iteration_detail} :material/arrow_forward: Iterasjon: {it}]")
            else:
                iteration_placeholder.markdown(f":red-badge[Iterasjon: {it}]")
        e_f, a_f, K_tot_star, status = maximize_remaining_production_capacity(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                                                              scenarios, with_tie_breakers=with_tie_breakers)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {"status": "INFEASABLE", "history": history}
        d_f, missile_cost_f, production_capacity = minimize_production_capacity(P_A, B_R, F, K_f, e_f, H_f, a_f)
        if d_f is None:
            return {"status": "SUBPROBLEM_INFEASABLE", "history": history}
        K_tot_gap = K_tot_star - production_capacity
        # If K_tot_star > production_capacity, a worse attack scenario has been found and K_tot_star needs to be recomputed
        history.append({
            "iteration": it,
            "established_facilities": e_f,
            "air_defense_assignment": a_f,
            "attack_scenario": d_f,
            "missile_costs": missile_cost_f,
            "remaining_production_capacity_after_attack": production_capacity,
            "previous_remaining_production_capacity": K_tot_star,
            "optimality_gap": K_tot_gap
        })
        if K_tot_gap <= 0:
            return {
                "status": "OPTIMAL",
                "established_facilities": e_f,
                "air_defense_assignment": a_f,
                "attack_scenario": d_f,
                "missile_costs": missile_cost_f,
                "remaining_production_capacity_after_attack": production_capacity,
                "optimality_gap": K_tot_gap,
                "history": history
            }
        scenarios.append(d_f) # Add new attack scenario and repeat
    return {"status": "MAX_ITERS_EXCEEDED", "history": history}