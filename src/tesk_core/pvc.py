from kubernetes import client, config
from kubernetes.client.rest import ApiException
from tesk_core.Util import pprint
import logging


class PVC():

    def __init__(self, name='task-pvc', size_gb=1, namespace='default'):
        self.name = name
        self.spec = {'apiVersion': 'v1',
                     'kind': 'PersistentVolumeClaim',
                     'metadata': {'name': name},
                     'spec': {
                         'accessModes': ['ReadWriteOnce'],
                         'resources': {'requests': {'storage': str(size_gb) + 'Gi'}},
                         # 'storageClassName': 'gold'
                     }
                     }

        self.subpath_idx = 0
        self.namespace = namespace
        self.cv1 = client.CoreV1Api()

    def set_volume_mounts(self, mounts):
        self.volume_mounts = mounts

    def get_subpath(self):
        subpath = 'dir' + str(self.subpath_idx)
        self.subpath_idx += 1
        return subpath
    
    def create(self):
        
        logging.debug('Creating PVC...')
        logging.debug(pprint(self.spec))
        try:
            return self.cv1.create_namespaced_persistent_volume_claim(self.namespace, self.spec)
        except ApiException as ex:
            if ex.status == 409:
                return self.cv1.read_namespaced_persistent_volume_claim(self.name, self.namespace)
            else:
                logging.error(ex.body)
                raise ApiException(ex.status, ex.reason)


    def delete(self):
        cv1 = client.CoreV1Api()
        cv1.delete_namespaced_persistent_volume_claim(
            self.name, self.namespace, body=client.V1DeleteOptions())
