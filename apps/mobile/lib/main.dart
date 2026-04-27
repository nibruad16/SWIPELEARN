import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:swipelearn/core/theme/app_theme.dart';
import 'package:swipelearn/screens/auth/auth_screen.dart';
import 'package:swipelearn/screens/feed/swipe_feed_screen.dart';
import 'package:swipelearn/screens/add_url/add_url_screen.dart';
import 'package:swipelearn/screens/teachers/teachers_screen.dart';
import 'package:swipelearn/screens/saved/saved_screen.dart';
import 'package:swipelearn/widgets/bottom_nav.dart';

/// SwipeLearn — Mobile-first learning app.
/// Transform blog posts into TikTok-style swipeable Knowledge Cards.

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Lock orientation to portrait
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);

  // Set status bar style
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: AppColors.surface,
    systemNavigationBarIconBrightness: Brightness.light,
  ));

  runApp(const SwipeLearnApp());
}

class SwipeLearnApp extends StatelessWidget {
  const SwipeLearnApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SwipeLearn',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const MainShell(),
    );
  }
}

/// MainShell — Root screen with bottom navigation.
/// Manages the 4 main tabs: Feed, Teachers, Add URL, Saved.

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;
  bool _isAuthenticated = true; // Set to false to show auth screen

  // Cache screens to preserve state
  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _screens = [
      const SwipeFeedScreen(),
      const TeachersScreen(),
      const AddUrlScreen(),
      const SavedScreen(),
    ];
  }

  void _onTabChanged(int index) {
    setState(() => _currentIndex = index);
    HapticFeedback.selectionClick();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isAuthenticated) {
      return AuthScreen(
        onAuthenticated: () {
          setState(() => _isAuthenticated = true);
        },
      );
    }

    return Scaffold(
      body: SafeArea(
        child: IndexedStack(
          index: _currentIndex,
          children: _screens,
        ),
      ),
      bottomNavigationBar: BottomNav(
        currentIndex: _currentIndex,
        onTap: _onTabChanged,
      ),
    );
  }
}
