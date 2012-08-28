import csp_solver
import os
csp_solver_config = csp_solver.get_valid_csp_solver_config(
    minisat_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'minisat')),
    sugarjar_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'sugar-v1-15-0.jar'))
)