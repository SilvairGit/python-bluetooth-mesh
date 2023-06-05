@Library('JenkinsMain@2.19.18')_

pipelinePythonSCA(
    agentLabel: 'docker',
    pythonVersion: '3.10',
    installFromSetup: true,
    packages: ['.[docs,tools,capnp]'],
    runPylint: false,
    runBlack: false,
    runIsort: false,
    runUnitTests: true,
    runLicensesChecks: false,
    alwaysPublish: false,
    unitTestRunner: 'python setup.py pytest'  // workaround until SP-10208 will be done
)
