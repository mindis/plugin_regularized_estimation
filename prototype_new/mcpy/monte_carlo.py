import os
import sys
import numpy as np
from joblib import Parallel, delayed
import joblib
import argparse
import importlib

def _check_valid_config(config):
    assert 'dgps' in config, "config dict must contain dgps"
    assert 'dgp_opts' in config, "config dict must contain dgp_opts"
    assert 'method_opts' in config, "config dict must contain method_opts"
    assert 'mc_opts' in config, "config dict must contain mc_opts"
    assert 'metrics' in config, "config dict must contain metrics"
    assert 'methods' in config, "config dict must contain methods"
    assert 'plots' in config, "config dict must contain plots"
    assert 'target_dir' in config, "config must contain target_dir"
    assert 'reload_results' in config, "config must contain reload_results"
    assert 'n_experiments' in config['mc_opts'], "config[mc_opts] must contain n_experiments"
    assert 'seed' in config['mc_opts'], "config[mc_opts] must contain seed"

class MonteCarlo:

    def __init__(self, config):
        self.config = config
        _check_valid_config(self.config)
        config['param_str'] = '_'.join(['{}_{}'.format(k, v) for k,v in self.config['mc_opts'].items()])
        config['param_str'] += '_' + '_'.join(['{}_{}'.format(k, v) for k,v in self.config['dgp_opts'].items()])
        config['param_str'] += '_' + '_'.join(['{}_{}'.format(k, v) for k,v in self.config['method_opts'].items()])
        return

    def experiment(self, exp_id):
        ''' Runs an experiment on a single randomly generated instance and sample and returns
        the parameter estimates for each method and the evaluated metrics for each method
        '''
        np.random.seed(exp_id)

        param_estimates = {}
        metric_results = {}
        for dgp_name, dgp_fn in self.config['dgps'].items():
            data, true_param = dgp_fn(self.config['dgp_opts'])
            param_estimates[dgp_name] = {}
            metric_results[dgp_name] = {}
            for method_name, method in self.config['methods'].items():
                param_estimates[dgp_name][method_name] = method(data, self.config['method_opts'])
                metric_results[dgp_name][method_name] = {}
                for metric_name, metric in self.config['metrics'].items():
                    metric_results[dgp_name][method_name][metric_name] = metric(param_estimates[dgp_name][method_name], true_param)

        return param_estimates, metric_results

    def run(self):
        ''' Runs multiple experiments in parallel on randomly generated instances and samples and returns
        the parameter estimates for each method and the evaluated metrics for each method across all
        experiments
        '''
        random_seed = self.config['mc_opts']['seed']

        if not os.path.exists(self.config['target_dir']):
            os.makedirs(self.config['target_dir'])

        results_file = os.path.join(self.config['target_dir'], 'results_{}.jbl'.format(self.config['param_str']))
        if self.config['reload_results'] and os.path.exists(results_file):
            results = joblib.load(results_file)
        else:
            results = Parallel(n_jobs=-1, verbose=1)(
                    delayed(self.experiment)(random_seed + exp_id)
                    for exp_id in range(self.config['mc_opts']['n_experiments']))
        joblib.dump(results, results_file)
        
        param_estimates = {}
        metric_results = {}
        for dgp_name in self.config['dgps'].keys():
            param_estimates[dgp_name] = {}
            metric_results[dgp_name] = {}
            for method_name in self.config['methods'].keys():
                param_estimates[dgp_name][method_name] = np.array([results[i][0][dgp_name][method_name] for i in range(self.config['mc_opts']['n_experiments'])])
                metric_results[dgp_name][method_name] = {}
                for metric_name in self.config['metrics'].keys():
                    metric_results[dgp_name][method_name][metric_name] = np.array([results[i][1][dgp_name][method_name][metric_name] for i in range(self.config['mc_opts']['n_experiments'])])
            
        for _, plot_fn in self.config['plots'].items():
            plot_fn(param_estimates, metric_results, self.config)

        return param_estimates, metric_results


def monte_carlo_main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--config', type=str, help='config file')
    args = parser.parse_args(sys.argv[1:])

    config = importlib.import_module(args.config)
    MonteCarlo(config.CONFIG).run()
    
if __name__=="__main__":
    monte_carlo_main()
    