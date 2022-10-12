# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from batchfold.batchfold_environment import BatchFoldEnvironment
from batchfold.omegafold_job import OmegaFoldJob
import pytest
import boto3
from datetime import datetime
import os

@pytest.fixture()
def batch_environment():
    stack = BatchFoldEnvironment(boto_session = boto3.Session())
    return(stack)

def test_omegafold_job_init():
    bucket = os.getenv("TEST_BUCKET")

    new_job = OmegaFoldJob(
        target_id = "T1084",
        fasta_s3_uri = f"s3://{bucket}/T1084/fasta/T1084.fasta",
        output_s3_uri = f"s3://{bucket}/T1084/outputs/"    
        )

    assert new_job.job_definition_name == "OmegaFoldJobDefinition"
    assert new_job.target_id == "T1084"
    assert new_job.fasta_s3_uri == f"s3://{bucket}/T1084/fasta/T1084.fasta"
    assert new_job.output_s3_uri == f"s3://{bucket}/T1084/outputs/"

def test_omegafold_job_submission(batch_environment):

    job_name = "OmegaFoldJob" + datetime.now().strftime("%Y%m%d%s")
    job_queue_name = "G4dnJobQueue"
    bucket = os.getenv("TEST_BUCKET")

    new_job = OmegaFoldJob(
        job_name = job_name,
        target_id = "T1084",
        fasta_s3_uri = f"s3://{bucket}/T1084/fasta/T1084.fasta",
        output_s3_uri = f"s3://{bucket}/T1084/outputs/",
    )

    submission = batch_environment.submit_job(new_job, job_queue_name)
    assert job_name == submission.job_name
    
    job_description = new_job.describe_job()        
    assert job_name == job_description[0].get("jobName", [])

    job_dict = batch_environment.list_jobs()
    job_list = job_dict[job_queue_name]
    assert len(job_list) > 0

    job_info = [job for job in job_list if job.get("jobName", []) == job_name]
    assert job_info[0].get("jobDefinition") == batch_environment.job_definitions["OmegaFoldJobDefinition"]
    assert job_info[0].get("jobName") == job_name