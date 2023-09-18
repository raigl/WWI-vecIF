#
code=~pi/wwi/Whirlwind-Instruction-Simulator/Code-Samples/
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
      3) p="wwsim";;
      4) p="wwsim $code/Bounce/r-196-bounce-example/bounce.acore";;
      5) p="wwsim $code/Mad-Game/mad-game.acore";;
      6) p="wwsim $code/Blackjack/bjack.acore";;
     15) exit;;
   esac
   echo "prog=$p"
   $p
done
                        
                        
 
