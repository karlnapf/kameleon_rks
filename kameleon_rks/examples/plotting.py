import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from kameleon_rks.tools.convergence_stats import autocorr


def pdf_grid(Xs, Ys, est):
    D = np.zeros((len(Xs), len(Ys)))
    G = np.zeros(D.shape)
    
    # this is in-efficient, log_pdf_multiple on a 2d array is faster
    for i, x in enumerate(Xs):
        for j, y in enumerate(Ys):
            point = np.array([x, y])
            D[j, i] = est.log_pdf(point)
            G[j, i] = np.linalg.norm(est.grad(point))
    
    return D, G

def visualise_fit_2d(est, X, Xs=None, Ys=None):
    # visualise found fit
    plt.figure()
    if Xs is None:
        Xs = np.linspace(-5, 5)
    
    if Ys is None:
        Ys = np.linspace(-5, 5)
    
    D, G = pdf_grid(Xs, Ys, est)
     
    plt.subplot(121)
    visualise_array(Xs, Ys, D, X)
    plt.title("log pdf")
     
    plt.subplot(122)
    visualise_array(Xs, Ys, G, X)
    plt.title("gradient norm")
    
    plt.tight_layout()

def visualise_array(Xs, Ys, A, samples=None):
    im = plt.imshow(A, origin='lower')
    im.set_extent([Xs.min(), Xs.max(), Ys.min(), Ys.max()])
    im.set_interpolation('nearest')
    im.set_cmap('gray')
    if samples is not None:
        plt.plot(samples[:, 0], samples[:, 1], 'bx')
    plt.ylim([Ys.min(), Ys.max()])
    plt.xlim([Xs.min(), Xs.max()])

def visualise_trajectory(Qs, acc_probs, log_pdf_q, D, log_pdf=None, Z=None, log_domain=True):
    assert Qs.ndim == 2
    
    plot_density = log_pdf is not None and D == 2
    
    plt.figure(figsize=(10, 12))
    plt.subplot(411)
    
    # plot density if given and dimension is 2
    if plot_density:
        Xs = np.linspace(-30, 30, 75)
        Ys = np.linspace(-10, 20, len(Xs))
        D, G = pdf_grid(Xs, Ys, log_pdf)
        if not log_domain:
            D = np.exp(D)
        visualise_array(Xs, Ys, D)
    
    plt.plot(Qs[:, 0], Qs[:, 1], 'r-', linewidth=2)
    plt.plot(Qs[0, 0], Qs[0, 1], 'r*', markersize=15)
    plt.title("Log-pdf surrogate")
        
    if Z is not None:
        plt.plot(Z[:, 0], Z[:, 1], 'b*')
    
    plt.subplot(412)
    if plot_density:
        visualise_array(Xs, Ys, G)
    plt.plot(Qs[:, 0], Qs[:, 1], 'r-', linewidth=2)
    plt.plot(Qs[0, 0], Qs[0, 1], 'r*', markersize=15)
            
    if Z is not None:
        plt.plot(Z[:, 0], Z[:, 1], 'b*')
        
    plt.title("Gradient norm surrogate")
    
    plt.subplot(413)
    plt.title("Acceptance probability")
    plt.xlabel("Leap frog iteration")
    plt.plot(acc_probs)
    plt.plot([0, len(acc_probs)], [np.mean(acc_probs) for _ in range(2)], 'r--')
    plt.xlim([0, len(acc_probs)])
    
    plt.subplot(414)
    plt.title("Target log-pdf")
    plt.xlabel("Leap frog iteration")
    plt.plot(log_pdf_q)
    plt.xlim([0, len(log_pdf_q)])

def visualise_pairwise_marginals(samples):
    df = pd.DataFrame(samples)
    pd.scatter_matrix(df, alpha=0.2, figsize=(8, 8), diagonal='kde', grid=True)

def visualize_scatter_2d(samples, step_sizes=None, acceptance_rates=None):
    assert samples.ndim == 2
    
    plt.figure()
    if step_sizes is not None or acceptance_rates is not None:
        plt.subplot(221, aspect='equal')
    plt.plot(samples[:, 0], samples[:, 1], 'bx')
    plt.grid(True)
    plt.title("Samples")
    
    if step_sizes is not None:
        plt.subplot(223)
        plt.title("Step sizes")
        plt.plot(step_sizes)
        plt.grid(True)
        plt.xlabel("Update iteration")
    
    if acceptance_rates is not None:
        plt.subplot(224)
        plt.title("Acceptanc rates")
        plt.plot(acceptance_rates)
        plt.grid(True)
        plt.xlabel("Update iteration")
    

def visualise_trace_2d(samples, log_pdf_trajectory, accepted, step_sizes=None, log_pdf_density=None, idx0=0, idx1=1):
    assert samples.ndim == 2
    
    D = samples.shape[1]
    
    plt.figure(figsize=(15, 12))
    
    plt.subplot(421)
    plt.plot(samples[:, idx0])
    plt.title("Trace $x_%d$" % (idx0 + 1))
    plt.xlabel("MCMC iteration")
    plt.grid(True)
    
    plt.subplot(422)
    plt.plot(samples[:, idx1])
    plt.title("Trace $x_%d$" % (idx1 + 1))
    plt.xlabel("MCMC iteration")
    plt.grid(True)
    
    plt.subplot(423)
    if not log_pdf_density is None and D == 2:
        Xs = np.linspace(-28, 28, 50)
        Ys = np.linspace(-6, 16, len(Xs))
        D, _ = pdf_grid(Xs, Ys, log_pdf_density)
        visualise_array(Xs, Ys, D)
        
    plt.plot(samples[:, idx0], samples[:, idx1])
    plt.title("Trace $(x_%d, x_%d)$" % (idx0 + 1, idx1 + 1))
    plt.grid(True)
    plt.xlabel("$x_%d$" % (idx0 + 1))
    plt.ylabel("$x_%d$" % (idx1 + 1))
    
    plt.subplot(424)
    plt.plot(log_pdf_trajectory)
    plt.title("log pdf along trajectory")
    plt.xlabel("MCMC iteration")
    plt.grid(True)
    
    plt.subplot(425)
    plt.plot(autocorr(samples[:, idx0]))
    plt.title("Autocorrelation $x_%d$" % (idx0 + 1))
    plt.xlabel("Lag")
    plt.grid(True)
    
    plt.subplot(426)
    plt.plot(autocorr(samples[:, idx1]))
    plt.title("Autocorrelation $x_%d$" % (idx1 + 1))
    plt.xlabel("Lag")
    plt.grid(True)
    
    plt.subplot(427)
    plt.plot(np.cumsum(accepted) / np.arange(1, len(accepted) + 1))
    plt.title("Average acceptance rate")
    plt.xlabel("MCMC iterations")
    plt.grid(True)
    
    if step_sizes is not None:
        plt.subplot(428)
        if step_sizes.ndim > 1:
            for i in range(step_sizes.shape[1]):
                plt.plot(step_sizes[:, i])
            plt.title("Step sizes")
        else:
            plt.plot(step_sizes)
            plt.title("Step size")
            
        plt.xlabel("MCMC iterations")
        plt.grid(True)
    plt.tight_layout()
