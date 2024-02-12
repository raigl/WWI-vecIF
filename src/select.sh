#
# cannot use $HOME or ~/ if started by crontab
#
wwsim=/home/pi/bin/wwsim
code=/home/pi/wwi/Whirlwind-Instruction-Simulator/Code-Samples
base=/home/pi/wwi/WWI-VecIF/src
examples=/home/pi/wwi/examples
wwim=/home/pi/wwi/Wh
while true
do $base/select.py
   rc=$?
   echo rc=$rc
   pwd
   p="continue"
   case $rc in
      0) continue;;
      1) p="$base/vecIF.py";;
      2) p="$base/tictactoe.py";;
      3) p="$wwsim $examples/lorenz.acore";;
      4) p="$wwsim $code/Bounce/r-196-bounce-example/bounce.acore";;
      5) p="$wwsim $code/Mad-Game/mad-game.acore";;
      6) p="$wwsim $code/Blackjack/bjack.acore";;
      7) p="$wwsim $code/Diags/crt-test-68_001_fbl00-0-50.tcore";;
      8) p="$wwsim $code/Vibrating-String/fb131-97-setup-and-run-Annotated.acore";;
      9) p="$wwsim $code/Vibrating-String/fc131-204-2-merged-annotated.acore";;
     10) p="$wwsim $code/Vibrating-String/fc131-204-6-merged-annotated.acore";;
     11) cd $code/Track-While-Scan-D-Israel/; p="$wwsim annotated-track-while-scan.acore -D -r --CrtF 5 --NoToggl --Ana -c 0 -q";;
     12) p="$wwsim $code/Number-Display/number-display-annotated";;
     13) p="$wwsim $code/CRT-Test-Guy/crt-test";;
     14) p="$wwsim $examples/vector-clock_rg";;
     15) exit;;
    127) exit;;
      *) continue;;
   esac
   echo "prog=$p"
   $p
done
                        
                        
