from IMLearn.learners.classifiers import Perceptron, LDA, GaussianNaiveBayes
from typing import Tuple
from utils import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import atan2, pi


def load_dataset(filename: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load dataset for comparing the Gaussian Naive Bayes and LDA classifiers. File is assumed to be an
    ndarray of shape (n_samples, 3) where the first 2 columns represent features and the third column the class
    Parameters
    ----------
    filename: str
        Path to .npy data file
    Returns
    -------
    X: ndarray of shape (n_samples, 2)
        Design matrix to be used
    y: ndarray of shape (n_samples,)
        Class vector specifying for each sample its class
    """
    data = np.load(filename)
    return data[:, :2], data[:, 2].astype(int)


def run_perceptron():
    """
    Fit and plot fit progression of the Perceptron algorithm over both the linearly separable and inseparable datasets
    Create a line plot that shows the perceptron algorithm's training loss values (y-axis)
    as a function of the training iterations (x-axis).
    """
    for n, f in [("Linearly Separable", "linearly_separable.npy"), ("Linearly Inseparable", "linearly_inseparable.npy")]:
        # Load dataset
        data = np.load(f"../datasets/{f}")
        X = data[:, :-1]
        y = data[:, -1]

        # Fit Perceptron and record loss in each fit iteration
        losses = []
        def loss_callback(estimator: Perceptron, _, __):
            a = estimator.loss(X, y)
            losses.append(a)

        perceptron = Perceptron(callback=loss_callback)
        perceptron.fit(X, y)

        # Plot figure of loss as function of fitting iteration
        fig = make_subplots()
        fig.add_trace(go.Scatter(x=np.arange(len(losses)), y=losses, mode='lines', name=n))

        fig.update_layout(
            title="Perceptron Training Loss Progression",
            xaxis_title="Iteration",
            yaxis_title="Training Loss",
            legend_title="Dataset"
        )
        fig.write_image(f"perceptron_fit_{n}.png")


def get_ellipse(mu: np.ndarray, cov: np.ndarray):
    """
    Draw an ellipse centered at given location and according to specified covariance matrix
    Parameters
    ----------
    mu : ndarray of shape (2,)
        Center of ellipse
    cov: ndarray of shape (2,2)
        Covariance of Gaussian
    Returns
    -------
        scatter: A plotly trace object of the ellipse
    """
    l1, l2 = tuple(np.linalg.eigvalsh(cov)[::-1])
    theta = atan2(l1 - cov[0, 0], cov[0, 1]) if cov[0, 1] != 0 else (np.pi / 2 if cov[0, 0] < cov[1, 1] else 0)
    t = np.linspace(0, 2 * pi, 100)
    xs = (l1 * np.cos(theta) * np.cos(t)) - (l2 * np.sin(theta) * np.sin(t))
    ys = (l1 * np.sin(theta) * np.cos(t)) + (l2 * np.cos(theta) * np.sin(t))

    return go.Scatter(x=mu[0] + xs, y=mu[1] + ys, mode="lines", marker_color="black")


def compare_gaussian_classifiers():
    """
    Fit both Gaussian Naive Bayes and LDA classifiers on both gaussians1 and gaussians2 datasets
    """
    for f in ["gaussian1.npy", "gaussian2.npy"]:
        # Load dataset
        data = np.load(f"../datasets/{f}")
        X = data[:, :-1]
        y = data[:, -1]

        # Fit models and predict over training set
        lda = LDA().fit(X, y)
        lda_prediction = lda.predict(X)
        gaussian_naive_bayes = GaussianNaiveBayes().fit(X,y)
        gaussian_naive_bayes_prediction = gaussian_naive_bayes.predict(X)

        # Plot a figure with two suplots, showing the Gaussian Naive Bayes predictions on the left and LDA predictions
        # on the right. Plot title should specify dataset used and subplot titles should specify algorithm and accuracy
        # Create subplots
        from IMLearn.metrics import accuracy
        # Calculate accuracy
        lda_accuracy = accuracy(y, lda_prediction)
        gaussian_naive_bayes_accuracy = accuracy(y, gaussian_naive_bayes_prediction)

        # Create subplots
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Gaussian Naive Bayes", "LDA"))

        # Add traces for data-points setting symbols and colors
        fig.add_trace(go.Scatter(x=X[:, 0], y=X[:, 1], mode='markers', marker=dict(color=y, symbol='circle'),
                                 name="Data Points"), row=1, col=1)
        fig.add_trace(go.Scatter(x=X[:, 0], y=X[:, 1], mode='markers', marker=dict(color=y, symbol='circle'),
                                 name="Data Points"), row=1, col=2)

        # Add `X` dots specifying fitted Gaussians' means
        means_lda = lda.mu_
        means_gaussian_naive_bayes = gaussian_naive_bayes.mu_
        fig.add_trace(go.Scatter(x=means_gaussian_naive_bayes[:, 0], y=means_gaussian_naive_bayes[:, 1],
                                 mode='markers', marker=dict(color='black', symbol='x'),
                                 name="Gaussian Naive Bayes Means"), row=1, col=1)
        fig.add_trace(go.Scatter(x=means_lda[:, 0], y=means_lda[:, 1], mode='markers',
                                 marker=dict(color='black', symbol='x'), name="LDA Means"), row=1, col=2)

        # Add ellipses depicting the covariances of the fitted Gaussians
        for i in range(3):
            fig.add_traces([get_ellipse(gaussian_naive_bayes.mu_[i],
                                        np.diag(gaussian_naive_bayes.vars_[i])), get_ellipse(lda.mu_[i], lda.cov_)],
                           rows=[1, 1], cols=[1, 2])

        fig.update_yaxes(scaleanchor="x", scaleratio=1)
        fig.update_layout(title_text=rf"$\text{{Comparing Gaussian Classifiers - {f[:-4]} dataset}}$",
                          width=1000, height=500, showlegend=False)
        fig.write_image(f"lda_and_gaussian_naive_bayes_comparison.{f[:-4]}.png")


if __name__ == '__main__':
    np.random.seed(0)
    run_perceptron()
    compare_gaussian_classifiers()