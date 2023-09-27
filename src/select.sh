#
code=~pi/wwi/Whirlwind-Instruction-Simulator/Code-Samples
base=~pi/wwi/WWI-VecIF/src
while true
do $base/select.py
   rc=$?
   echo rc=$rc
   p="continue"
   case $rc in
      0) continue;;
      1) p="$base/vecIF.py";;
      2) p="$base/tictactoe.py";;
      3) continue;;
      4) p="wwsim $code/Bounce/r-196-bounce-example/bounce.acore";;
      5) p="wwsim $code/Mad-Game/mad-game.acore";;
      6) p="wwsim $code/Blackjack/bjack.acore";;
      7) p="wwsim $code/Diags/crt-test-68_001_fbl00-0-50.tcore";;
      8) p="wwsim $code/Vibrating-String/fb131-97-setup-and-run-Annotated.acore";;
      9) p="wwsim $code/Vibrating-String/fc131-204-2-merged-annotated.acore";;
     10) p="wwsim $code/Vibrating-String/fc131-204-6-merged-annotated.acore";;
     11) p="wwsim $code/Track-While-Scan-D-Israel/annotated-track-while-scan.acore -D -r --CrtF 5 --NoToggl --Ana -c 0 -q";;
     15) exit;;
    127) exit;;
      *) continue;;
   esac
   echo "prog=$p"
   $p
done
                        
                        
