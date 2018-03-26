import os
import google.cloud.storage
import configargparse
import logging
import glob


def get_last_file(path):
    """
    :param dir:
    :return: terates through all files that are under the given path and
    returns last created/edited file
    """

    list_of_files = glob.glob(path + '*')
    return max(list_of_files, key=os.path.getctime)


def run(root_dir, bucket_name, bucket_dir):
    """
    Simple script which fetches last generated blueprint and uploads
    """
    logger = logging.getLogger(__name__)
    logger.info('Starting to upload blueprints to gcp bucket: ' + bucket_name +
                ', bucket_dir: ' + bucket_dir)

    # Get last modified/created blueprint file
    last_blueprint_file = get_last_file(root_dir)
    logger.info('last_blueprint_file:' + last_blueprint_file)

    # Create a storage client.
    source_file_name = last_blueprint_file
    storage_client = google.cloud.storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(bucket_dir + os.path.basename(source_file_name))
    blob.upload_from_filename(source_file_name)
    logger.info('File ' + source_file_name + ' uploaded to ' + str(bucket))


if __name__ == '__main__':
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--path', help='Path to root dir from where the script should read files (default out/blueprints)')
    arg_parser.add('--bucket', help='GCP Bucket name and path', required=True)
    arg_parser.add('--bucket_dir', help='GCP Bucket directory')

    args = arg_parser.parse_known_args()[0]

    if args.path is None:
        args.path = '../out/blueprints/'
    run(root_dir=args.path, bucket_name=args.bucket, bucket_dir=args.bucket_dir)
