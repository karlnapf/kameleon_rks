import time

from kameleon_rks.tools.log import Log
import numpy as np


logger = Log.get_logger()

def mini_mcmc(transition_kernel, start, num_iter, D, recompute_log_pdf=False, time_budget=None):
    # MCMC results
    samples = np.zeros((num_iter, D)) + np.nan
    proposals = np.zeros((num_iter, D)) + np.nan
    accepted = np.zeros(num_iter) + np.nan
    acc_prob = np.zeros(num_iter) + np.nan
    log_pdf = np.zeros(num_iter) + np.nan
    step_sizes = np.zeros(num_iter) + np.nan
    
    # timings for output and time limit
    times = np.zeros(num_iter)
    last_time_printed = time.time()
    
    # for adaptive transition kernels
    avg_accept = 0.
    
    # init MCMC (first iteration)
    current = start
    current_log_pdf = None
    current_kwargs = {}
    
    logger.info("Starting MCMC using %s in D=%d dimensions" % \
                (transition_kernel.get_name(), D,))
    
    for it in range(num_iter):
        times[it] = time.time()
        
        # stop sampling if time budget exceeded
        if time_budget is not None:
            if times[it] > times[0] + time_budget:
                logger.info("Time limit of %ds exceeded. Stopping MCMC at iteration %d." % (time_budget, it))
                break
        
        # print chain progress
        if times[it] > last_time_printed + 5:
            log_str = "MCMC iteration %d/%d, current log_pdf: %.6f, avg acceptance: %.3f, step_size_ %.3f" % (it + 1, num_iter,
                                                                       np.nan if log_pdf[it - 1] is None else log_pdf[it - 1],
                                                                       avg_accept, transition_kernel.step_size)
            last_time_printed = times[it]
            logger.info(log_str)
        
        # marginal sampler: make transition kernel re-compute log_pdf of current state
        if recompute_log_pdf:
            current_log_pdf = None
        
        # generate proposal and acceptance probability
        logger.debug("Performing MCMC step %d" % it)
        proposals[it], prop_target_log_pdf, current_log_pdf, forw_log_pdf, backw_logpdf, current_kwargs = transition_kernel.proposal(current, current_log_pdf, **current_kwargs)
        
        acc_prob[it] = transition_kernel.mh(current_log_pdf, prop_target_log_pdf, backw_logpdf, forw_log_pdf)
        
        # accept-reject
        r = np.random.rand()
        accepted[it] = r < acc_prob[it]
        
        logger.debug("Proposed %s" % str(proposals[it]))
        logger.debug("Acceptance prob %.4f" % acc_prob[it])
        logger.debug("Accepted: %d" % accepted[it])
        
        
        # update running mean according to knuth's stable formula
        avg_accept += (accepted[it] - avg_accept) / (it + 1)
        
        # update state
        logger.debug("Updating chain")
        if accepted[it]:
            current = proposals[it]
            current_log_pdf = prop_target_log_pdf

        # store sample
        samples[it] = current
        log_pdf[it] = current_log_pdf
        
        # update transition kernel, might do nothing
        transition_kernel.next_iteration()
        
        # make all samples available
        transition_kernel.update(samples[:(it+1)])
        
        transition_kernel.update_step_size(acc_prob[:(it+1)])
        
        # store step size
        step_sizes[it] = transition_kernel.step_size
        
    # recall it might be less than last iterations due to time budget
    return samples[:it], proposals[:it], accepted[:it], acc_prob[:it], log_pdf[:it], times[:it], step_sizes[:it]
