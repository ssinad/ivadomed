import os
import pytest
import csv_diff
import logging
import torch
from testing.unit_tests.t_utils import create_tmp_dir, __data_testing_dir__, __tmp_dir__, download_data_testing_test_files, path_repo_root
from testing.common_testing_util import remove_tmp_dir
from ivadomed.loader import utils as imed_loader_utils
from ivadomed.loader import loader as imed_loader
logger = logging.getLogger(__name__)


def setup_function():
    create_tmp_dir()


@pytest.mark.parametrize('loader_parameters', [{
    "path_data": [os.path.join(__data_testing_dir__, "microscopy_png")],
    "bids_config": f"{path_repo_root}/ivadomed/config/config_bids.json",
    "target_suffix": [["_seg-myelin-manual", "_seg-axon-manual"]],
    "extensions": [".png"],
    "roi_params": {"suffix": None, "slice_filter_roi": None},
    "contrast_params": {"contrast_lst": []}
    }])
def test_bids_df_microscopy_png(download_data_testing_test_files, loader_parameters):
    """
    Test for microscopy png file format
    Test for _sessions.tsv and _scans.tsv files
    Test for target_suffix as a nested list
    Test for when no contrast_params are provided
    """

    bids_df = imed_loader_utils.BidsDataframe(loader_parameters, __tmp_dir__, derivatives=True)
    df_test = bids_df.df.drop(columns=['path'])
    df_test = df_test.sort_values(by=['filename']).reset_index(drop=True)
    csv_ref = os.path.join(loader_parameters["path_data"][0], "df_ref.csv")
    csv_test = os.path.join(loader_parameters["path_data"][0], "df_test.csv")
    df_test.to_csv(csv_test, index=False)
    diff = csv_diff.compare(csv_diff.load_csv(open(csv_ref)), csv_diff.load_csv(open(csv_test)))
    assert diff == {'added': [], 'removed': [], 'changed': [], 'columns_added': [], 'columns_removed': []}


@pytest.mark.parametrize('loader_parameters', [{
    "path_data": [__data_testing_dir__],
    "target_suffix": ["_lesion-manual"],
    "extensions": [],
    "roi_params": {"suffix": "_seg-manual", "slice_filter_roi": None},
    "contrast_params": {"contrast_lst": ["T1w", "T2w"]}
    }])
def test_bids_df_anat(download_data_testing_test_files, loader_parameters):
    """
    Test for MRI anat nii.gz file format
    Test for when no file extensions are provided
    Test for multiple target_suffix
    Test behavior when "roi_suffix" is not None
    """

    bids_df = imed_loader_utils.BidsDataframe(loader_parameters, __tmp_dir__, derivatives=True)
    df_test = bids_df.df.drop(columns=['path'])
    df_test = df_test.sort_values(by=['filename']).reset_index(drop=True)
    csv_ref = os.path.join(loader_parameters["path_data"][0], "df_ref.csv")
    csv_test = os.path.join(loader_parameters["path_data"][0], "df_test.csv")
    df_test.to_csv(csv_test, index=False)
    diff = csv_diff.compare(csv_diff.load_csv(open(csv_ref)), csv_diff.load_csv(open(csv_test)))
    assert diff == {'added': [], 'removed': [], 'changed': [],
                    'columns_added': [], 'columns_removed': []}


@pytest.mark.parametrize('loader_parameters', [{
    "path_data": [__data_testing_dir__, os.path.join(__data_testing_dir__, "microscopy_png")],
    "bids_config": f"{path_repo_root}/ivadomed/config/config_bids.json",
    "target_suffix": ["_seg-manual", "seg-axon-manual"],
    "extensions": [".nii.gz", ".png"],
    "roi_params": {"suffix": None, "slice_filter_roi": None},
    "contrast_params": {"contrast_lst": ["T1w", "T2w", "SEM"]}
    }])
def test_bids_df_multi(download_data_testing_test_files, loader_parameters):
    """
    Test for multiple folders in path_data
    """

    bids_df = imed_loader_utils.BidsDataframe(loader_parameters, __tmp_dir__, derivatives=True)
    df_test = bids_df.df.drop(columns=['path'])
    df_test = df_test.sort_values(by=['filename']).reset_index(drop=True)
    csv_ref = os.path.join(loader_parameters["path_data"][0], "df_ref_multi.csv")
    csv_test = os.path.join(loader_parameters["path_data"][0], "df_test_multi.csv")
    df_test.to_csv(csv_test, index=False)
    diff = csv_diff.compare(csv_diff.load_csv(open(csv_ref)), csv_diff.load_csv(open(csv_test)))
    assert diff == {'added': [], 'removed': [], 'changed': [],
                    'columns_added': [], 'columns_removed': []}


@pytest.mark.parametrize('loader_parameters', [{
    "path_data": [os.path.join(__data_testing_dir__, "ct_scan")],
    "bids_config": f"{path_repo_root}/ivadomed/config/config_bids.json",
    "target_suffix": ["_seg-manual"],
    "extensions": [".nii.gz"],
    "roi_params": {"suffix": None, "slice_filter_roi": None},
    "contrast_params": {"contrast_lst": ["ct"]}
    }])
def test_bids_df_ctscan(download_data_testing_test_files, loader_parameters):
    """
    Test for ct-scan nii.gz file format
    Test for when dataset_description.json is not present in derivatives folder
    """

    bids_df = imed_loader_utils.BidsDataframe(loader_parameters, __tmp_dir__, derivatives=True)
    df_test = bids_df.df.drop(columns=['path'])
    df_test = df_test.sort_values(by=['filename']).reset_index(drop=True)
    csv_ref = os.path.join(loader_parameters["path_data"][0], "df_ref.csv")
    csv_test = os.path.join(loader_parameters["path_data"][0], "df_test.csv")
    df_test.to_csv(csv_test, index=False)
    diff = csv_diff.compare(csv_diff.load_csv(open(csv_ref)), csv_diff.load_csv(open(csv_test)))
    assert diff == {'added': [], 'removed': [], 'changed': [], 'columns_added': [], 'columns_removed': []}


@pytest.mark.parametrize('seg_pair', [
    {"input": torch.rand((2, 5, 5))},
    {"input": torch.rand((1, 5, 5))},
    {"input": torch.rand((5, 5, 5, 5))},
    {"input": (torch.rand((5, 5, 5, 3)) * torch.tensor([1, 0, 1], dtype=torch.float)).transpose(0, -1)},
    {"input": (torch.rand((7, 7, 4)) * torch.tensor([1, 0, 0, 0], dtype=torch.float)).transpose(0, -1)}
])
def test_dropout_input(seg_pair):
    n_channels = seg_pair['input'].size(0)
    seg_pair = imed_loader.dropout_input(seg_pair)
    empty_channels = [len(torch.unique(input_data)) == 1 for input_data in seg_pair['input']]

    # If multichannel
    if n_channels > 1:
        # Verify that there is still at least one channel remaining
        assert sum(empty_channels) <= n_channels
    else:
        assert sum(empty_channels) == 0


@pytest.mark.parametrize('loader_parameters', [{
    "path_data": [os.path.join(__data_testing_dir__, "microscopy_png")],
    "bids_config": f"{path_repo_root}/ivadomed/config/config_bids.json",
    "target_suffix": ["_seg-myelin-manual"],
    "extensions": [".png"],
    "roi_params": {"suffix": None, "slice_filter_roi": None},
    "contrast_params": {"contrast_lst": [], "balance": {}},
    "slice_axis": "axial",
    "slice_filter_params": {"filter_empty_mask": False, "filter_empty_input": True},
    "multichannel": False
    }])
@pytest.mark.parametrize('model_parameters', [{
    "name": "Unet",
    "dropout_rate": 0.3,
    "bn_momentum": 0.1,
    "final_activation": "sigmoid",
    "depth": 3
    }])
@pytest.mark.parametrize('transform_parameters', [{
    "NumpyToTensor": {},
    }])
def test_load_dataset_2d_png(download_data_testing_test_files,
                             loader_parameters, model_parameters, transform_parameters):
    """
    Test to make sure load_dataset runs with 2D PNG data.
    """
    loader_parameters.update({"model_params": model_parameters})
    bids_df = imed_loader_utils.BidsDataframe(loader_parameters, __tmp_dir__, derivatives=True)
    data_lst = ['sub-rat3_ses-01_sample-data9_SEM.png']
    ds = imed_loader.load_dataset(bids_df,
                                  **{**loader_parameters, **{'data_list': data_lst,
                                                             'transforms_params': transform_parameters,
                                                             'dataset_type': 'training'}})
    assert ds[0]['input'].shape == (1, 756, 764)
    assert ds[0]['gt'].shape == (1, 756, 764)


@pytest.mark.parametrize('loader_parameters', [{
    "path_data": [os.path.join(__data_testing_dir__, "microscopy_png")],
    "bids_config": f"{path_repo_root}/ivadomed/config/config_bids.json",
    "target_suffix": ["_seg-myelin-manual"],
    "extensions": [".png"],
    "roi_params": {"suffix": None, "slice_filter_roi": None},
    "contrast_params": {"contrast_lst": [], "balance": {}},
    "slice_axis": "axial",
    "slice_filter_params": {"filter_empty_mask": False, "filter_empty_input": True},
    "multichannel": False
    }])
@pytest.mark.parametrize('model_parameters', [{
    "name": "Unet",
    "dropout_rate": 0.3,
    "bn_momentum": 0.1,
    "final_activation": "sigmoid",
    "depth": 3,
    "length_2D": [256, 256],
    "stride_2D": [244, 244]
    }])
@pytest.mark.parametrize('transform_parameters', [{
    "Resample": {
        "wspace": 0.0001,
        "hspace": 0.0001
    },
    "NumpyToTensor": {},
    }])
def test_2d_patches(download_data_testing_test_files,
                    loader_parameters, model_parameters, transform_parameters):
    """
    Test to make sure load_dataset runs with 2D PNG data.
    """
    loader_parameters.update({"model_params": model_parameters})
    bids_df = imed_loader_utils.BidsDataframe(loader_parameters, __tmp_dir__, derivatives=True)
    data_lst = ['sub-rat3_ses-01_sample-data9_SEM.png']
    ds = imed_loader.load_dataset(bids_df,
                                  **{**loader_parameters, **{'data_list': data_lst,
                                                             'transforms_params': transform_parameters,
                                                             'dataset_type': 'training'}})

    assert ds.is_2d_patch == True
    assert ds[0]['input'].shape == (1, 256, 256)
    assert len(ds) == 16


def teardown_function():
    remove_tmp_dir()
