Configuration File
==================

General parameters
------------------

command
~~~~~~~

Run the specified command. Choices: ``"train"``, ``"test"``, ``"eval"``,
to train, test and evaluate a model respectively.

gpu
^^^

Integer. ID of the GPU to use.

log\_directory
^^^^^^^^^^^^^^

Folder name that will contain the output files (e.g., trained model,
predictions, results).

debugging
^^^^^^^^^

Bool. Extended verbosity and intermediate outputs.

Loader parameters
-----------------

bids\_path
^^^^^^^^^^

String. Path of the BIDS folder.

target\_suffix
^^^^^^^^^^^^^^

List. Suffix list of the derivative file containing the ground-truth of
interest (e.g. [``"_seg-manual"``, ``"_lesion-manual"``]). The length of
this list controls the number of output channels of the model (i.e.
``out_channel``). If the list has a length greater than 1, then a
multi-class model will be trained.

contrasts
^^^^^^^^^

-  ``train_validation``: List. List of image contrasts (e.g. ``T1w``,
   ``T2w``) loaded for the training and validation. If ``multichannel``
   is ``true``, this list represents the different channels of the input
   tensors (i.e. its length equals model's ``in_channel``). Otherwise,
   the contrasts are mixed and the model has only one input channel
   (i.e. model's ``in_channel=1``).
-  ``test``: List. List of image contrasts (e.g. ``T1w``, ``T2w``)
   loaded in the testing dataset. Same comment than for
   ``train_validation`` regarding ``multichannel``.
-  ``balance``: Dict. Enables to weight the importance of specific
   channels (or contrasts) in the dataset: e.g. ``{"T1w": 0.1}`` means
   that only 10% of the available ``T1w`` images will be included into
   the training/validation/test set. Please set ``multichannel`` to
   ``false`` if you are using this parameter.

multichannel
^^^^^^^^^^^^

Bool. Indicated if more than a contrast (e.g. ``T1w`` and ``T2w``) is
used by the model. See details in both ``train_validation`` and ``test``
for the contrasts that are input.

slice\_axis
^^^^^^^^^^^

Choice between ``"sagittal"``, ``"coronal"``, and ``"axial"``. Sets the
slice orientation for on which the model will be used.

slice\_filter
^^^^^^^^^^^^^

Dict. Discard a slice from the dataset if it meets a condition, see
below. - ``filter_empty_input``: Bool. Discard slices where all voxel
intensities are zeros. - ``filter_empty_mask``: Bool. Discard slices
where all voxel labels are zeros.

roi
^^^

Dict. of parameters about the region of interest - ``suffix``: String.
Suffix of the derivative file containing the ROI used to crop (e.g.
``"_seg-manual"``) with ``ROICrop`` as transform. Please use ``null`` if
you do not want to use an ROI to crop. - ``slice_filter_roi``: int. If
the ROI mask contains less than ``slice_filter_roi`` non-zero voxels,
the slice will be discarded from the dataset. This feature helps with
noisy labels, e.g., if a slice contains only 2-3 labeled voxels, we do
not want to use these labels to crop the image. This parameter is only
considered when using ``"ROICrop"``.

Split dataset
-------------

fname\_split
^^^^^^^^^^^^

String. File name of the log
(`joblib <https://joblib.readthedocs.io/en/latest/>`__) that contains
the list of training/validation/testing subjects. This file can later be
used to re-train a model using the same data splitting scheme. If
``null``, a new splitting scheme is performed.

random\_seed
^^^^^^^^^^^^

Int. Seed used by the random number generator to split the dataset
between training/validation/testing. The use of the same seed ensures
the same split between the sub-datasets, which is useful to reproduce
results.

method
^^^^^^

``{"per_patient", "per_center"}``. ``"per_patient"``: all subjects are
shuffled, then split between train/validation/test according to
``"train_fraction"`` and ``"test_fraction"``, regardless their
institution. ``"per_center"``: all subjects are split so as not to mix
institutions between the train/validation/test sets according to
``"train_fraction"`` and ``"center_test"``. The latter option enables to
ensure the model is working across domains (institutions). Note: the
institution information is contained within the ``institution_id``
column in the ``participants.tsv`` file.

train\_fraction
^^^^^^^^^^^^^^^

Float. Between ``0`` and ``1`` representing the fraction of the dataset
used as training set.

test\_fraction
^^^^^^^^^^^^^^

Float. Between ``0`` and ``1`` representing the fraction of the dataset
used as test set. This parameter is only used if the ``method`` is
``"per_patient"``.

center\_test
^^^^^^^^^^^^

List of strings. Each string corresponds to an institution/center to
only include in the testing dataset (not validation). This parameter is
only used if the ``method`` is ``"per_center"``. If used, the file
``bids_dataset/participants.tsv`` needs to contain a column
``institution_id``, which associates a subject with an
institution/center.

Training parameters
-------------------

batch\_size
^^^^^^^^^^^

Strictly positive integer.

loss
^^^^

- ``name``: Name of the loss function class. See :mod:`ivadomed.losses`
-  Other parameters that could be needed in the Loss function
   definition: see attributes of the Loss function of interest (e.g.
   ``"gamma": 0.5`` for ``FocalLoss``).

training\_time
^^^^^^^^^^^^^^

-  ``num_epochs``: Strictly positive integer.
-  ``early_stopping_epsilon``: Float. If the validation loss difference
   during one epoch (i.e.
   ``abs(validation_loss[n] - validation_loss[n-1]`` where n is the
   current epoch) is inferior to this epsilon for
   ``early_stopping_patience`` consecutive epochs, then training stops.
-  ``early_stopping_patience``: Strictly positive integer. Number of
   epochs after which the training is stopped if the validation loss
   improvement is smaller than ``early_stopping_epsilon``.

scheduler
^^^^^^^^^

-  ``initial_lr``: Float. Initial learning rate.
-  ``scheduler_lr``:

1. ``name``: Choice between: ``"CosineAnnealingLR"``,
   ``"CosineAnnealingWarmRestarts"`` and ``"CyclicLR"``. Please find
   documentation `here <https://pytorch.org/docs/stable/optim.html>`__.
2. Other parameters that are needed for the scheduler of interest (e.g.
   ``"base_lr": 1e-5, "max_lr": 1e-2`` for ``"CosineAnnealingLR"``).

balance\_samples
^^^^^^^^^^^^^^^^

Bool. Balance positive and negative labels in both the training and the
validation datasets.

mixup\_alpha
^^^^^^^^^^^^

Float. Alpha parameter of the Beta distribution, see `original paper on
the Mixup technique <https://arxiv.org/abs/1710.09412>`__.

transfer\_learning
^^^^^^^^^^^^^^^^^^

-  ``retrain_model``: Filename of the pretrained model
   (``path/to/pretrained-model``). If ``null``, no transfer learning is
   performed and the network is trained from scratch.
-  ``retrain_fraction``: Float between 0. and 1. Controls the fraction
   of the pre-trained model that will be fine-tuned. For instance, if
   set to 0.5, the second half of the model will be fine-tuned while the
   first layers will be frozen.

Architecture
------------

Architectures for both segmentation and classification are available and
described in the :ref:`models:Models` section. If the selected
architecture is listed in the
`loader.py <../../ivadomed/loader/loader.py#L14>`__ FIXME file, a
classification (not segmentation) task is run. In the case of a
classification task, the ground truth will correspond to a single label
value extracted from ``target``, instead being an array (the latter
being used for the segmentation task).

default\_model (Mandatory)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Dict. Define the default model (``Unet``) and mandatory parameters that
are common to all available architectures (listed in the
:ref:`models:Models` section). For more specific models (see below),
the default parameters are merged with the parameters that are specific
to the tailored model. - ``name``: ``Unet`` (default) -
``dropout_rate``: Float (e.g. 0.4). - ``batch_norm_momentum``: Float
(e.g. 0.1). - ``depth``: Strictly positive integer. Number of
down-sampling operations.

FiLMedUnet (Optional)
~~~~~~~~~~~~~~~~~~~~~

-  ``applied``: Bool. Set to ``true`` to use this model.
-  ``metadata``: String. Choice between ``"mri_params"`` or
   ``"contrast"``. ``"mri_params"``: Vectors of
   ``[FlipAngle, EchoTime, RepetitionTime, Manufacturer]`` (defined in
   the json of each image) are input to the FiLM generator.
   ``"contrast"``: Image contrasts (according to
   ``config/contrast_dct.json``) are input to the FiLM generator.

HeMISUnet (Optional)
~~~~~~~~~~~~~~~~~~~~

-  ``applied``: Bool. Set to ``true`` to use this model.
-  ``missing_probability``: Float between 0 and 1. Initial probability
   of missing image contrasts as model's input (e.g. 0.25 results in a
   quarter of the image contrasts, i.e. channels, that will not been
   sent to the model for training).
-  ``missing_probability_growth``: Float. Controls missing probability
   growth at each epoch: at each epoch, the ``missing_probability`` is
   modified with the exponent ``missing_probability_growth``.

UNet3D (Optional)
~~~~~~~~~~~~~~~~~

-  ``length_3D``: (Int, Int, Int). Size of the 3D patches used as
   model's input tensors.
-  ``attention_unet``: Bool. Use attention gates in the Unet's decoder.

Testing parameters
------------------

-  ``binarize_prediction``: Bool. Binarize output predictions using a
   threshold of 0.5. If ``false``, output predictions are float between
   0 and 1.

uncertainty
^^^^^^^^^^^

Uncertainty computation is performed if ``n_it>0`` and at least
``epistemic`` or ``aleatoric`` is ``true``. Note: both ``epistemic`` and
``aleatoric`` can be ``true``. - ``epistemic``: Bool. Model-based
uncertainty with `Monte Carlo
Dropout <https://arxiv.org/abs/1506.02142>`__. - ``aleatoric``: Bool.
Image-based uncertainty with `test-time
augmentation <https://doi.org/10.1016/j.neucom.2019.01.103>`__. -
``n_it``: Integer. Number of Monte Carlo iterations. Set to 0 for no
uncertainty computation.

Transformations
---------------

Transformations applied during data augmentation. Transformations are
sorted in the order they are applied to the image samples. For each
transformation, the following parameters are customizable: -
``applied_to``: list betweem ``"im", "gt", "roi"``. If not specified,
then the transformation is applied to all loaded samples. Otherwise,
only applied to the specified types: eg ``["gt"]`` implies that this
transformation is only applied to the ground-truth data. -
``dataset_type``: list between ``"training", "validation", "testing"``.
If not specified, then the transformation is applied to the three
sub-datasets. Otherwise, only applied to the specified subdatasets: eg
``["testing"]`` implies that this transformation is only applied to the
testing sub-dataset.

Available transformations:
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``NumpyToTensor``
-  ``CenterCrop2D`` (parameters: ``size``)
-  ``ROICrop2D`` (parameters: ``size``)
-  ``NormalizeInstance``
-  ``RandomRotation`` (parameters: ``degrees``)
-  ``RandomAffine`` (parameters: ``translate``)
-  ``RandomShiftIntensity`` (parameters: ``shift_range``)
-  ``ElasticTransform`` (parameters: ``alpha_range``, ``sigma_range``,
   ``p``)
-  ``Resample`` (parameters: ``wspace``, ``hspace``, ``dspace``)
-  ``AdditionGaussianNoise`` (parameters: ``mean``, ``std``)
-  ``DilateGT`` (parameters: ``dilation_factor``) Float. Controls the
   number of iterations of ground-truth dilation depending on the size
   of each individual lesion, data augmentation of the training set. Use
   ``0`` to disable.
-  ``HistogramClipping`` (parameters: ``min_percentile``,
   ``max_percentile``)
-  ``Clage`` (parameters: ``clip_limit``, ``kernel_size``)
-  ``RandomReverse``

Examples
--------

Examples of configuration files: `here <../../ivadomed/config>`__ FIXME.

In particular: -
`config\_classification.json <../../ivadomed/config/config_classification.json>`__ FIXME
is dedicated to classification task. -
`config\_sctTesting.json <../../ivadomed/config/config_sctTesting.json>`__ FIXME
is a user case of 2D segmentation using a U-Net model. -
`config\_spineGeHemis.json <../../ivadomed/config/config_spineGeHemis.json>`__ FIXME
shows how to use the HeMIS-UNet. -
`config\_tumorSeg.json <../../ivadomed/config/config_tumorSeg.json>`__ FIXME
runs a 3D segmentation using a 3D UNet.