
The files in this directory implement three types of classifier algorithms:

- BinaryLogisticRegressionClassifier.py
- BinaryNearestMeanClassifier.py
- BinaryNearestNeighborClassifier.py

The implementation of every classifier is split in a "Factory" function that produces the classifier,
as well as a "Classifier" class that is able to yield scores of a given collection of samples.

=== Organization of the classes ===

Each classififier algorithm defines two classes: a "Factory" and a "Classifier" class.

- The "Factory" class is constructed with parameters that are necessary for the training process.
  An example is the distance metric for the NMC classifier, or the back-end algorithm of the
  LogisticRegression classifier.

- A classifier factory has a "train" method that takes feature values and class labels.
  This method performs the training, and returns an actual, concrete "Classifier" instance.

- The 'Classifier' classes have a 'score' method that returns the score of a given collection
  of samples.

The separation in a 'Factory' class and an actual 'Classifier' class may seem strange at first,
but it makes software engineering sense; both Factory and Classifier instances are *immutable*
objects, i.e., objects that do not change state after construction time. This makes them easier to
understand and work with.
