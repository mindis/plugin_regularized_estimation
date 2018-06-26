import numpy as np
import linear_te
import metrics

CONFIG = {
        "opts": {'n_experiments': 100, # number of monte carlo experiments
            'n_samples': 5000, # samples used for estimation
            'dim_x': 200, # dimension of controls x
            'dim_z': 200, # dimension of variables used for heterogeneity (subset of x)
            'kappa_theta': 2, # support size of target parameter
            'kappa_x': 38, # support size of nuisance
            'sigma_eta': 1.0, # variance of error in secondary moment equation
            'sigma_epsilon': 1.0, # variance of error in primary moment equation
            'lambda_coef': 1.0 # coeficient in front of the asymptotic rate for regularization lambda
        },
        "methods": {
            "Direct": linear_te.direct_fit,
            "Ortho": linear_te.dml_fit,
            "CrossOrtho": linear_te.dml_crossfit
        },
        "metrics": {
            "$\\ell_2$ error": metrics.l2_error,
            "$\\ell_1$ error": metrics.l1_error
        },
        "mc_opts": {
            "target_dir": "results_linear",
            "reload_results": True,
            "plot_params": False,
            "random_seed": 123,
            "proposed_method": "CrossOrtho",
            "gen_data": linear_te.gen_data
        }
    }