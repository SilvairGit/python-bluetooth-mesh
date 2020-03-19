@Library('JenkinsMain@2.16.16')_

pipelinePythonSCA(
    agentLabel: 'pylint',
    pythonVersion: '3.6',
    packages: ['.[tools]'],
    runUnitTests: true,
    runBlack: true,
    runIsort: true,
    installFromSetup: true,
    unitTestRunner: './test.sh'
)
