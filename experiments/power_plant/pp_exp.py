"""
Power Plant
"""

from collections import OrderedDict

from experiments.experiment import Experiment
from models.hmc_samplers import HMCSampler, SGHMCSampler
from models.ld_samplers import LDSampler, SGLDSampler, pSGLDSampler
from experiments.power_plant.pp_env import PowerPlantEnv


class PowerPlantExp(Experiment):
    def __init__(self):
        super().__init__()

    def _setup_sampler_defaults(self, sampler_params):
        sampler_params['noise_precision'] = 5.
        sampler_params['weights_precision'] = 1.

    def run_baseline_hmc(self):
        env = PowerPlantEnv()
        self.setup_env_defaults(env)

        env.model_name = 'hmc'
        env.test_case_name = 'baseline'

        env.chains_num = 10
        env.n_samples = 10
        env.thinning = 0

        sampler_params = dict()
        sampler_params['step_sizes'] = .0005
        sampler_params['hmc_steps'] = 10
        sampler_params['mh_correction'] = True

        sampler_params['batch_size'] = None
        sampler_params['seek_step_sizes'] = False
        sampler_params['fade_in_velocities'] = True
        env.setup_data_dir()
        self.configure_env_mcmc(env, HMCSampler, sampler_params)
        env.run()

    def run_sgld(self):
        env = PowerPlantEnv()
        self.setup_env_defaults(env)

        env.model_name = 'sgld'

        env.n_samples = 100
        env.thinning = 3

        sampler_params = dict()
        sampler_params['step_sizes'] = .001

        sampler_params['fade_in_velocities'] = True

        env.setup_data_dir()
        self.configure_env_mcmc(env, SGLDSampler, sampler_params)
        env.run()

    def run_sghmc(self):
        env = PowerPlantEnv()
        self.setup_env_defaults(env)

        env.model_name = 'sghmc'

        env.chains_num = 1
        env.n_samples = 50
        env.thinning = 0

        sampler_params = dict()
        sampler_params['step_sizes'] = .0005
        sampler_params['hmc_steps'] = 25
        sampler_params['friction'] = 1.

        sampler_params['fade_in_velocities'] = True

        env.setup_data_dir()
        self.configure_env_mcmc(env, SGHMCSampler, sampler_params)
        env.run()

    def run_psgld(self):
        env = PowerPlantEnv()
        self.setup_env_defaults(env)

        env.model_name = 'psgld'

        env.n_samples = 100
        env.thinning = 4

        sampler_params = dict()
        sampler_params['step_sizes'] = .001
        sampler_params['preconditioned_alpha'] = .999
        sampler_params['preconditioned_lambda'] = .01

        sampler_params['fade_in_velocities'] = True

        env.setup_data_dir()
        self.configure_env_mcmc(env, pSGLDSampler, sampler_params)
        env.run()

    def run_dropout(self):
        env = PowerPlantEnv()
        self.setup_env_defaults(env)

        env.model_name = 'dropout'

        env.n_samples = 40

        sampler_params = dict()
        sampler_params['n_epochs'] = 5

        dropout = 0.05
        tau = 0.087

        env.setup_data_dir()
        self.configure_env_dropout(env, sampler_params=sampler_params, dropout=dropout, tau=tau)
        env.run()

    def run_pbp(self):
        env = PowerPlantEnv()
        self.setup_env_defaults(env)

        env.model_name = 'pbp'
        env.n_samples = 1000
        env.n_chunks = 10

        env.setup_data_dir()
        self.configure_env_pbp(env, n_epochs=4)
        env.run()


def main():
    experiment = PowerPlantExp()

    queue = OrderedDict()
    queue['HMC'] = experiment.run_baseline_hmc
    queue['SGLD'] = experiment.run_sgld
    queue['SGHMC'] = experiment.run_sghmc
    queue['pSGLD'] = experiment.run_psgld
    # queue["PBP"] = experiment.run_pbp
    queue['Dropout'] = experiment.run_dropout

    experiment.run_queue(queue, cpu=False)
    experiment.report_metrics_table(queue)

    del queue['HMC']

    max_time = 15
    experiment.plot_multiple_metrics('HMC', queue.keys(), ['KS'], max_time=max_time, title_name='KS distance')
    experiment.plot_multiple_metrics('HMC', queue.keys(), ['Precision'], max_time=max_time, title_name='Precision')
    experiment.plot_multiple_metrics('HMC', queue.keys(), ['Recall'], max_time=max_time, title_name='Recall')
    # experiment.plot_multiple_metrics("HMC", queue.keys(), ["KL"])
    # experiment.plot_multiple_metrics("HMC", queue.keys(), ["F1"], max_time=max_time, title_name="F1 score")
    # experiment.plot_multiple_metrics("HMC", queue.keys(), ["IoU"], max_time=max_time)


if __name__ == '__main__':
    main()
