from setuptools import setup

setup(name='AWSIoTDeviceDefenderAgentSDK',
      version='1.1.1',
      description='AWS IoT Device Defender Agent SDK',
      url='https://github.com/aws-samples/aws-iot-device-defender-agent-sdk-python',
      author='Amazon Web Services',
      author_email='aws-iot-device-defender@amazon.com',
      license='APACHE.20',
      packages=['AWSIoTDeviceDefenderAgentSDK'],
      install_requires=[
          'psutil',
          'cbor',
          'AWSIoTPythonSDK'
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'
      ],
      zip_safe=False
      )
