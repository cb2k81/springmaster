# 000157 springmaster transactional validation environment isolation

- keeps transaction-child control variables private to the patch engine;
- sanitizes tooling, test, full-test and export subprocess environments;
- makes the transactional acceptance integration test robust inside an outer validation worktree;
- adds a regression proving nested tooling sees no internal transaction flags.
