# Usage
- Compile and tuning instructions found in README, which is from the original repository that was forked from.
- Best frequency for me is 433.542e6, which is for an Efergy Elite Classic
- to use the python code to process output, pipe the output from, so something like
  ```
    rtl_fm -f 433.542e6 -s 200000 -r 96000 -A fast 2>/dev/null | ./EfergyRPI_log | python3 process_efergy.py
  ```

# Other notes
- can't remember how I installed rtl_fm :(
