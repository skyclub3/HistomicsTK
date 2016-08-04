import pandas as pd
from skimage.measure import regionprops

from .ComputeFSDFeatures import ComputeFSDFeatures
from .ComputeGradientFeatures import ComputeGradientFeatures
from .ComputeIntensityFeatures import ComputeIntensityFeatures
from .ComputeMorphometryFeatures import ComputeMorphometryFeatures

from histomicstk.segmentation import label as htk_label


def ExtractNuclearFeatures(im_label, im_nuclei, im_cytoplasm=None,
                           fsd_k=128, fsd_freq_bins=6, cyto_width=8,
                           morphometry_features_flag=True,
                           fsd_features_flag=True,
                           intensity_features_flag=True,
                           gradient_features_flag=True
                           ):
    """
    Calculates features for nuclei classification

    Parameters
    ----------
    im_label : array_like
        A labeled mask image wherein intensity of a pixel is the ID of the
        object it belongs to. Non-zero values are considered to be foreground
        objects.

    im_nuclei : array_like
        Nucleus channel intensity image.

    im_cytoplasm : array_like
        Cytoplasm channel intensity image.

    fsd_k : int, optional
        Number of points for boundary resampling to calculate fourier
        descriptors. Default value = 128.

    fsd_freq_bins : int, optional
        Number of frequency bins for calculating FSDs. Default value = 6.

    cyto_width : float, optional
        Estimated width of the ring-like neighborhood region around each
        nucleus to be considered as its cytoplasm. Default value = 8.

    morphometry_features_flag : bool, optional
        A flag that can be used to specify whether or not to compute
        morphometry (size and shape) features.
        See histomicstk.features.ComputeMorphometryFeatures for more details.

    fsd_features_flag : bool, optional
        A flag that can be used to specify whether or not to compute
        Fouried shape descriptor (FSD) features.
        See `histomicstk.features.ComputeFSDFeatures` for more details.

    intensity_features_flag : bool, optional
        A flag that can be used to specify whether or not to compute
        intensity features from the nucleus and cytoplasm channels.
        See `histomicstk.features.ComputeFSDFeatures` for more details.

    gradient_features_flag : bool, optional
        A flag that can be used to specify whether or not to compute
        gradient/edge features from intensity and cytoplasm channels.
        See `histomicstk.features.ComputeGradientFeatures` for more details.

    Returns
    -------
    fdata : pandas.DataFrame
        A pandas data frame containing the features listed below for each
        object/label

    Notes
    -----
    List of features computed by this function

    Morphometry (size and shape) features of the nuclei
        See histomicstk.features.ComputeMorphometryFeatures for more details.
        Feature names prefixed by *Size.* or *Shape.*.

    Fourier shape descriptor features
        See `histomicstk.features.ComputeFSDFeatures` for more details.
        Feature names are prefixed by *FSD*.

    Intensity features for the nucleus and cytoplasm channels
        See `histomicstk.features.ComputeFSDFeatures` for more details.
        Feature names are prefixed by *Nucleus.Intensity.* for nucleus features
        and *Cytoplasm.Intensity.* for cytoplasm features.

    Gradient/edge features for the nucleus and cytoplasm channels
        See `histomicstk.features.ComputeGradientFeatures` for more details.
        Feature names are prefixed by *Nucleus.Gradient.* for nucleus features
        and *Cytoplasm.Gradient.* for cytoplasm features.

    See Also
    --------
    histomicstk.features.ComputeMorphometryFeatures,
    histomicstk.features.ComputeFSDFeatures,
    histomicstk.features.ComputeIntensityFeatures,
    histomicstk.features.ComputeGradientFeatures,
    """

    feature_list = []

    # get the number of objects in im_label
    nuclei_props = regionprops(im_label)

    # compute cytoplasm mask
    if im_cytoplasm is not None:

        cyto_mask = htk_label.ComputeNeighborhoodMask(im_label,
                                                      neigh_width=cyto_width)

        cytoplasm_props = regionprops(cyto_mask)

    # compute morphometry features
    if morphometry_features_flag:

        fmorph = ComputeMorphometryFeatures(im_label, rprops=nuclei_props)

        feature_list.append(fmorph)

    # compute FSD features
    if fsd_features_flag:

        ffsd = ComputeFSDFeatures(im_label, fsd_k, fsd_freq_bins, cyto_width,
                                  rprops=nuclei_props)

        feature_list.append(ffsd)

    # compute nuclei intensity features
    if intensity_features_flag:

        fint_nuclei = ComputeIntensityFeatures(im_label, im_nuclei,
                                               rprops=nuclei_props)
        fint_nuclei.columns = ['Nucleus.' + col
                               for col in fint_nuclei.columns]

        feature_list.append(fint_nuclei)

    # compute cytoplasm intensity features
    if intensity_features_flag and im_cytoplasm is not None:

        fint_cytoplasm = ComputeIntensityFeatures(cyto_mask, im_cytoplasm)
        fint_cytoplasm.columns = ['Cytoplasm.' + col
                                  for col in fint_cytoplasm.columns]

        feature_list.append(fint_cytoplasm)

    # compute nuclei gradient features
    if gradient_features_flag:

        fgrad_nuclei = ComputeGradientFeatures(im_label, im_nuclei,
                                               rprops=nuclei_props)
        fgrad_nuclei.columns = ['Nucleus.' + col
                                for col in fgrad_nuclei.columns]

        feature_list.append(fgrad_nuclei)

    # compute cytoplasm gradient features
    if gradient_features_flag and im_cytoplasm is not None:

        fgrad_cytoplasm = ComputeGradientFeatures(cyto_mask, im_cytoplasm)
        fgrad_cytoplasm.columns = ['Cytoplasm.' + col
                                   for col in fgrad_cytoplasm.columns]

        feature_list.append(fgrad_cytoplasm)

    # Merge all features
    fdata = pd.concat(feature_list, axis=1)

    return fdata
